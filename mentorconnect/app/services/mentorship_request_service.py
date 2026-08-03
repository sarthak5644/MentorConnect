"""
app/services/mentorship_request_service.py
-------------------------------------------------
Business logic for students sending mentorship requests and mentors
accepting/rejecting them. On acceptance, automatically creates the Chat
thread so messaging can begin immediately.
"""

from typing import List, Optional
from datetime import datetime

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundException, ConflictException, BadRequestException
from app.models.enums import (
    MentorshipRequestStatus, MentorApprovalStatus, NotificationType, AuditAction,
)
from app.models.mentorship_request import MentorshipRequest
from app.models.student import Student
from app.models.mentor import Mentor
from app.repositories.mentorship_request_repository import MentorshipRequestRepository
from app.repositories.mentor_repository import MentorRepository
from app.repositories.chat_repository import ChatRepository
from app.services.notification_service import NotificationService
from app.services.audit_service import AuditService
from app.utils.sanitizer import sanitize_text
from app.schemas.mentorship_request import MentorshipRequestCreate, MentorshipRequestRespond


class MentorshipRequestService:
    def __init__(self, db: Session):
        self.db = db
        self.request_repo = MentorshipRequestRepository(db)
        self.mentor_repo = MentorRepository(db)
        self.chat_repo = ChatRepository(db)
        self.notification_service = NotificationService(db)
        self.audit_service = AuditService(db)

    def create_request(self, student: Student, payload: MentorshipRequestCreate) -> MentorshipRequest:
        mentor = self.mentor_repo.get(payload.mentor_id)
        if mentor is None:
            raise NotFoundException("Mentor not found.")

        if mentor.approval_status != MentorApprovalStatus.APPROVED:
            raise BadRequestException("This mentor is not currently available for mentorship requests.")

        if not mentor.is_accepting_requests:
            raise BadRequestException("This mentor is not currently accepting new mentorship requests.")

        existing = self.request_repo.get_pending_between(student.id, mentor.id)
        if existing is not None:
            raise ConflictException("You already have a pending request with this mentor.")

        request = self.request_repo.create({
            "student_id": student.id,
            "mentor_id": mentor.id,
            "message": sanitize_text(payload.message),
            "status": MentorshipRequestStatus.PENDING,
        })

        self.notification_service.notify(
            mentor.user_id, NotificationType.MENTORSHIP_REQUEST,
            "New mentorship request received",
            body=f"{student.user.full_name if student.user else 'A student'} sent you a mentorship request.",
            reference_id=request.id,
        )
        return request

    def respond_to_request(
        self, mentor: Mentor, request_id: int, payload: MentorshipRequestRespond
    ) -> MentorshipRequest:
        request = self.request_repo.get(request_id)
        if request is None or request.mentor_id != mentor.id:
            raise NotFoundException("Mentorship request not found.")

        if request.status != MentorshipRequestStatus.PENDING:
            raise ConflictException(f"This request has already been {request.status.value}.")

        if payload.status not in (MentorshipRequestStatus.ACCEPTED, MentorshipRequestStatus.REJECTED):
            raise BadRequestException("Response status must be 'accepted' or 'rejected'.")

        request.status = payload.status
        request.response_note = sanitize_text(payload.response_note)
        request.responded_at = datetime.utcnow()
        self.db.add(request)
        self.db.commit()
        self.db.refresh(request)

        if payload.status == MentorshipRequestStatus.ACCEPTED:
            # Auto-create the chat thread so messaging can start right away
            self.chat_repo.create({"mentorship_request_id": request.id, "is_active": True})

        student_user_id = request.student.user_id if request.student else None
        if student_user_id:
            title = (
                "Your mentorship request was accepted!"
                if payload.status == MentorshipRequestStatus.ACCEPTED
                else "Your mentorship request was declined"
            )
            self.notification_service.notify(
                student_user_id, NotificationType.MENTORSHIP_REQUEST, title,
                body=payload.response_note, reference_id=request.id,
            )

        self.audit_service.log(
            AuditAction.UPDATE, entity_type="MentorshipRequest", entity_id=request.id,
            description=f"Mentor responded: {payload.status.value}",
        )
        return request

    def cancel_request(self, student: Student, request_id: int) -> MentorshipRequest:
        request = self.request_repo.get(request_id)
        if request is None or request.student_id != student.id:
            raise NotFoundException("Mentorship request not found.")
        if request.status != MentorshipRequestStatus.PENDING:
            raise ConflictException("Only pending requests can be cancelled.")

        request.status = MentorshipRequestStatus.CANCELLED
        request.responded_at = datetime.utcnow()
        self.db.add(request)
        self.db.commit()
        self.db.refresh(request)
        return request

    def list_for_student(self, student_id: int, skip: int = 0, limit: int = 20) -> List[MentorshipRequest]:
        return self.request_repo.list_by_student(student_id, skip, limit)

    def list_for_mentor(
        self, mentor_id: int, status: Optional[MentorshipRequestStatus] = None, skip: int = 0, limit: int = 20
    ) -> List[MentorshipRequest]:
        return self.request_repo.list_by_mentor(mentor_id, status, skip, limit)
