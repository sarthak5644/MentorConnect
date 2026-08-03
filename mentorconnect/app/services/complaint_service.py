"""
app/services/complaint_service.py
-------------------------------------
Business logic for students filing complaints and admins resolving them.
"""

from typing import List, Optional
from datetime import datetime

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundException, ConflictException, BadRequestException
from app.models.enums import ComplaintStatus, NotificationType, AuditAction
from app.models.complaint import Complaint
from app.models.student import Student
from app.models.user import User
from app.repositories.complaint_repository import ComplaintRepository
from app.services.notification_service import NotificationService
from app.services.audit_service import AuditService
from app.utils.sanitizer import sanitize_text
from app.schemas.complaint import ComplaintCreateRequest, ComplaintResolveRequest


class ComplaintService:
    def __init__(self, db: Session):
        self.db = db
        self.complaint_repo = ComplaintRepository(db)
        self.notification_service = NotificationService(db)
        self.audit_service = AuditService(db)

    def create_complaint(self, student: Student, payload: ComplaintCreateRequest) -> Complaint:
        complaint = self.complaint_repo.create({
            "student_id": student.id,
            "against_user_id": payload.against_user_id,
            "booking_id": payload.booking_id,
            "subject": sanitize_text(payload.subject),
            "description": sanitize_text(payload.description),
            "status": ComplaintStatus.OPEN,
        })
        return complaint

    def resolve_complaint(self, admin: User, complaint_id: int, payload: ComplaintResolveRequest) -> Complaint:
        complaint = self.complaint_repo.get(complaint_id)
        if complaint is None:
            raise NotFoundException("Complaint not found.")

        if complaint.status in (ComplaintStatus.RESOLVED, ComplaintStatus.DISMISSED):
            raise ConflictException("This complaint has already been closed.")

        if payload.status not in (ComplaintStatus.RESOLVED, ComplaintStatus.DISMISSED, ComplaintStatus.IN_REVIEW):
            raise BadRequestException("Invalid resolution status.")

        complaint.status = payload.status
        complaint.admin_notes = sanitize_text(payload.admin_notes)
        if payload.status in (ComplaintStatus.RESOLVED, ComplaintStatus.DISMISSED):
            complaint.resolved_by_admin_id = admin.id
            complaint.resolved_at = datetime.utcnow()

        self.db.add(complaint)
        self.db.commit()
        self.db.refresh(complaint)

        if complaint.student and complaint.student.user_id:
            self.notification_service.notify(
                complaint.student.user_id, NotificationType.COMPLAINT,
                f"Your complaint has been {payload.status.value}",
                body=payload.admin_notes, reference_id=complaint.id,
            )

        self.audit_service.log(
            AuditAction.UPDATE, actor_user_id=admin.id, entity_type="Complaint",
            entity_id=complaint.id, description=f"Complaint {payload.status.value} by admin",
        )
        return complaint

    def list_for_student(self, student_id: int, skip: int = 0, limit: int = 20) -> List[Complaint]:
        return self.complaint_repo.list_by_student(student_id, skip, limit)

    def list_all(self, status: Optional[ComplaintStatus] = None, skip: int = 0, limit: int = 20) -> List[Complaint]:
        return self.complaint_repo.list_all(status, skip, limit)
