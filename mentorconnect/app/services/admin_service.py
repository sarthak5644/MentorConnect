"""
app/services/admin_service.py
---------------------------------
Business logic for Super Admin operations: blocking/unblocking users,
dashboard KPI summary, and analytics/report aggregation.
"""

from datetime import datetime
from collections import defaultdict
from typing import List, Optional, Dict

from sqlalchemy import select, func, extract
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundException, BadRequestException, ConflictException
from app.models.enums import (
    UserStatus, RoleName, MentorApprovalStatus, BookingStatus, ComplaintStatus, AuditAction,
    NotificationType,
)
from app.models.user import User, Role
from app.models.mentor import Mentor
from app.repositories.user_repository import UserRepository, RoleRepository
from app.repositories.mentor_repository import MentorRepository
from app.repositories.mentorship_request_repository import MentorshipRequestRepository
from app.repositories.booking_repository import BookingRepository
from app.repositories.complaint_repository import ComplaintRepository
from app.services.audit_service import AuditService
from app.services.notification_service import NotificationService
from app.utils.sanitizer import sanitize_text
from app.schemas.dashboard import DashboardSummary, AnalyticsReport, MonthlySignupPoint, TopMentorPoint


class AdminService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.role_repo = RoleRepository(db)
        self.mentor_repo = MentorRepository(db)
        self.request_repo = MentorshipRequestRepository(db)
        self.booking_repo = BookingRepository(db)
        self.complaint_repo = ComplaintRepository(db)
        self.audit_service = AuditService(db)
        self.notification_service = NotificationService(db)

    # ------------------------------------------------------------------
    # User management
    # ------------------------------------------------------------------
    def block_user(self, admin: User, user_id: int, reason: str) -> User:
        user = self.user_repo.get(user_id)
        if user is None:
            raise NotFoundException("User not found.")
        if user.role.name == RoleName.SUPER_ADMIN:
            raise BadRequestException("Cannot block a Super Admin account.")
        if user.status == UserStatus.BLOCKED:
            raise ConflictException("User is already blocked.")

        user.status = UserStatus.BLOCKED
        user.blocked_at = datetime.utcnow()
        user.blocked_reason = sanitize_text(reason)
        user.token_version += 1  # force logout from all sessions
        self.db.add(user)
        self.db.commit()

        self.notification_service.notify(
            user.id, NotificationType.ACCOUNT, "Your account has been blocked", body=reason,
        )
        self.audit_service.log(
            AuditAction.BLOCK, actor_user_id=admin.id, entity_type="User",
            entity_id=user.id, description=f"User blocked: {reason}",
        )
        return user

    def unblock_user(self, admin: User, user_id: int) -> User:
        user = self.user_repo.get(user_id)
        if user is None:
            raise NotFoundException("User not found.")
        if user.status != UserStatus.BLOCKED:
            raise ConflictException("User is not currently blocked.")

        user.status = UserStatus.ACTIVE
        user.blocked_at = None
        user.blocked_reason = None
        self.db.add(user)
        self.db.commit()

        self.notification_service.notify(
            user.id, NotificationType.ACCOUNT, "Your account has been unblocked",
            body="You can now log in and use MentorConnect again.",
        )
        self.audit_service.log(
            AuditAction.UNBLOCK, actor_user_id=admin.id, entity_type="User",
            entity_id=user.id, description="User unblocked",
        )
        return user

    def list_users(self, status: Optional[UserStatus] = None, skip: int = 0, limit: int = 20) -> List[User]:
        if status is not None:
            return self.user_repo.list_by_status(status, skip, limit)
        return self.user_repo.get_all(skip, limit)

    # ------------------------------------------------------------------
    # Dashboard / Analytics
    # ------------------------------------------------------------------
    def get_dashboard_summary(self) -> DashboardSummary:
        total_users = self.user_repo.count_all()
        total_students = self._count_users_by_role(RoleName.STUDENT)
        total_mentors = self._count_users_by_role(RoleName.MENTOR)
        pending_mentor_approvals = self.mentor_repo.count_by_approval_status(MentorApprovalStatus.PENDING)
        total_bookings = self.booking_repo.count_all()
        completed_bookings = self.booking_repo.count_by_status(BookingStatus.COMPLETED)
        total_requests = self.request_repo.count_all()
        open_complaints = self.complaint_repo.count_by_status(ComplaintStatus.OPEN)
        blocked_users = self.user_repo.count_by_status(UserStatus.BLOCKED)

        return DashboardSummary(
            total_users=total_users,
            total_students=total_students,
            total_mentors=total_mentors,
            pending_mentor_approvals=pending_mentor_approvals,
            total_bookings=total_bookings,
            completed_bookings=completed_bookings,
            total_mentorship_requests=total_requests,
            open_complaints=open_complaints,
            blocked_users=blocked_users,
        )

    def _count_users_by_role(self, role_name: RoleName) -> int:
        """Counts users with a given role via an explicit join (avoids relying on lazy-loaded relationship comparisons)."""
        stmt = (
            select(func.count())
            .select_from(User)
            .join(Role, User.role_id == Role.id)
            .where(Role.name == role_name)
        )
        return self.db.execute(stmt).scalar_one()

    def get_analytics_report(self) -> AnalyticsReport:
        signups = self._signups_by_month()
        top_mentors = self._top_mentors()
        bookings_by_status = self.booking_repo.count_grouped_by_status()
        complaints_by_status = self.complaint_repo.count_grouped_by_status()

        return AnalyticsReport(
            signups_by_month=signups,
            top_mentors=top_mentors,
            bookings_by_status=bookings_by_status,
            complaints_by_status=complaints_by_status,
        )

    def _signups_by_month(self) -> List[MonthlySignupPoint]:
        """Aggregates user signups per month, split by student/mentor role."""
        stmt = (
            select(
                extract("year", User.created_at).label("y"),
                extract("month", User.created_at).label("m"),
                User.role_id,
                func.count().label("cnt"),
            )
            .group_by("y", "m", User.role_id)
            .order_by("y", "m")
        )
        rows = self.db.execute(stmt).all()

        student_role = self.role_repo.get_by_name(RoleName.STUDENT)
        mentor_role = self.role_repo.get_by_name(RoleName.MENTOR)

        buckets: Dict[str, Dict[str, int]] = defaultdict(lambda: {"students": 0, "mentors": 0})
        for year, month, role_id, count in rows:
            key = f"{int(year):04d}-{int(month):02d}"
            if student_role and role_id == student_role.id:
                buckets[key]["students"] += count
            elif mentor_role and role_id == mentor_role.id:
                buckets[key]["mentors"] += count

        return [
            MonthlySignupPoint(month=k, students=v["students"], mentors=v["mentors"])
            for k, v in sorted(buckets.items())
        ]

    def _top_mentors(self, limit: int = 10) -> List[TopMentorPoint]:
        stmt = (
            select(Mentor, User.full_name)
            .join(User, Mentor.user_id == User.id)
            .order_by(Mentor.average_rating.desc(), Mentor.total_sessions_completed.desc())
            .limit(limit)
        )
        rows = self.db.execute(stmt).all()
        return [
            TopMentorPoint(
                mentor_id=mentor.id, full_name=full_name,
                average_rating=mentor.average_rating,
                total_sessions_completed=mentor.total_sessions_completed,
            )
            for mentor, full_name in rows
        ]
