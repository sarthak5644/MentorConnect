"""
app/services/mentor_service.py
----------------------------------
Business logic for mentor profile management, document uploads, availability
slots, and the admin approval/rejection workflow.
"""

import json
from typing import List, Optional, Tuple
from datetime import datetime

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundException, BadRequestException, ConflictException
from app.models.enums import MentorApprovalStatus, DocumentStatus, AuditAction, NotificationType, SlotStatus
from app.models.mentor import Mentor
from app.models.user import User
from app.repositories.mentor_repository import MentorRepository
from app.repositories.mentor_document_repository import MentorDocumentRepository
from app.repositories.slot_repository import SlotRepository
from app.repositories.category_repository import FieldRepository
from app.services.file_upload_service import FileUploadService
from app.services.notification_service import NotificationService
from app.services.audit_service import AuditService
from app.services.email_service import EmailService
from app.utils.sanitizer import sanitize_text
from app.schemas.mentor import (
    MentorProfileUpdate, MentorQualificationsUpdate, MentorAchievementsUpdate, MentorSearchFilters,
)
from app.schemas.availability_slot import SlotCreateRequest


class MentorService:
    def __init__(self, db: Session):
        self.db = db
        self.mentor_repo = MentorRepository(db)
        self.document_repo = MentorDocumentRepository(db)
        self.slot_repo = SlotRepository(db)
        self.field_repo = FieldRepository(db)
        self.notification_service = NotificationService(db)
        self.audit_service = AuditService(db)

    def get_mentor_or_404(self, mentor_id: int) -> Mentor:
        mentor = self.mentor_repo.get_with_relations(mentor_id)
        if mentor is None:
            raise NotFoundException("Mentor not found.")
        return mentor

    def get_mentor_by_user(self, user: User) -> Mentor:
        mentor = self.mentor_repo.get_by_user_id(user.id)
        if mentor is None:
            raise NotFoundException("Mentor profile not found for this account.")
        return mentor

    # ------------------------------------------------------------------
    # Profile management
    # ------------------------------------------------------------------
    def update_profile(self, mentor: Mentor, payload: MentorProfileUpdate) -> Mentor:
        data = payload.model_dump(exclude_unset=True)
        if "bio" in data:
            data["bio"] = sanitize_text(data["bio"])
        if "headline" in data:
            data["headline"] = sanitize_text(data["headline"])
        if "linkedin_url" in data and data["linkedin_url"] is not None:
            data["linkedin_url"] = str(data["linkedin_url"])
        if "portfolio_url" in data and data["portfolio_url"] is not None:
            data["portfolio_url"] = str(data["portfolio_url"])

        for field, value in data.items():
            setattr(mentor, field, value)
        self.db.add(mentor)
        self.db.commit()
        self.db.refresh(mentor)
        return mentor

    def update_qualifications(self, mentor: Mentor, payload: MentorQualificationsUpdate) -> Mentor:
        mentor.qualifications = json.dumps([q.model_dump() for q in payload.qualifications])
        self.db.add(mentor)
        self.db.commit()
        self.db.refresh(mentor)
        return mentor

    def update_achievements(self, mentor: Mentor, payload: MentorAchievementsUpdate) -> Mentor:
        mentor.achievements = json.dumps([a.model_dump() for a in payload.achievements])
        self.db.add(mentor)
        self.db.commit()
        self.db.refresh(mentor)
        return mentor

    def update_expertise(self, mentor: Mentor, field_ids: List[int]) -> Mentor:
        fields = self.field_repo.get_many_by_ids(field_ids)
        if len(fields) != len(set(field_ids)):
            raise BadRequestException("One or more field IDs are invalid.")
        mentor.expertise_fields = fields
        self.db.add(mentor)
        self.db.commit()
        self.db.refresh(mentor)
        return mentor

    async def upload_profile_image(self, user: User, file: UploadFile) -> str:
        relative_path = await FileUploadService.upload_profile_image(file)
        user.profile_image_url = relative_path
        self.db.add(user)
        self.db.commit()
        return relative_path

    # ------------------------------------------------------------------
    # Documents
    # ------------------------------------------------------------------
    async def upload_document(self, mentor: Mentor, document_type: str, file: UploadFile):
        relative_path, ext, size_bytes = await FileUploadService.upload_mentor_document(file)
        document = self.document_repo.create({
            "mentor_id": mentor.id,
            "document_type": sanitize_text(document_type),
            "file_name": file.filename,
            "file_path": relative_path,
            "file_size_bytes": size_bytes,
            "mime_type": ext,
            "status": DocumentStatus.PENDING,
        })
        return document

    def list_documents(self, mentor_id: int):
        return self.document_repo.list_by_mentor(mentor_id)

    # ------------------------------------------------------------------
    # Availability Slots
    # ------------------------------------------------------------------
    def create_slot(self, mentor: Mentor, payload: SlotCreateRequest):
        if payload.start_time <= datetime.utcnow():
            raise BadRequestException("Slot start time must be in the future.")

        overlapping = self.slot_repo.get_overlapping(mentor.id, payload.start_time, payload.end_time)
        if overlapping:
            raise ConflictException("This slot overlaps with an existing availability slot.")

        return self.slot_repo.create({
            "mentor_id": mentor.id,
            "start_time": payload.start_time,
            "end_time": payload.end_time,
        })

    def create_bulk_slots(self, mentor: Mentor, slots: List[SlotCreateRequest]):
        created = []
        for slot_payload in slots:
            created.append(self.create_slot(mentor, slot_payload))
        return created

    def list_slots(self, mentor_id: int, status=None, upcoming_only: bool = True):
        from_time = datetime.utcnow() if upcoming_only else None
        return self.slot_repo.list_by_mentor(mentor_id, status=status, from_time=from_time)

    def delete_slot(self, mentor: Mentor, slot_id: int) -> None:
        slot = self.slot_repo.get(slot_id)
        if slot is None or slot.mentor_id != mentor.id:
            raise NotFoundException("Slot not found.")
        if slot.status == SlotStatus.BOOKED:
            raise ConflictException("Cannot delete a slot that is already booked.")
        self.slot_repo.delete(slot)

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------
    def search_mentors(self, filters: MentorSearchFilters, skip: int, limit: int) -> Tuple[List[Mentor], int]:
        return self.mentor_repo.search(filters, skip, limit)

    # ------------------------------------------------------------------
    # Admin: Approval Workflow
    # ------------------------------------------------------------------
    def list_pending_approval(self, skip: int = 0, limit: int = 20) -> List[Mentor]:
        return self.mentor_repo.list_pending_approval(skip, limit)

    async def approve_mentor(self, mentor_id: int, admin: User, notes: Optional[str] = None) -> Mentor:
        mentor = self.get_mentor_or_404(mentor_id)
        if mentor.approval_status == MentorApprovalStatus.APPROVED:
            raise ConflictException("Mentor is already approved.")

        mentor.approval_status = MentorApprovalStatus.APPROVED
        mentor.approved_by_admin_id = admin.id
        mentor.approved_at = datetime.utcnow()
        mentor.rejection_reason = None
        self.db.add(mentor)
        self.db.commit()
        self.db.refresh(mentor)

        self.notification_service.notify(
            mentor.user_id, NotificationType.ACCOUNT, "Your mentor profile has been approved!",
            body=notes or "You can now start accepting mentorship requests.",
            reference_id=mentor.id,
        )
        self.audit_service.log(
            AuditAction.APPROVE, actor_user_id=admin.id, entity_type="Mentor",
            entity_id=mentor.id, description="Mentor approved by admin",
        )
        await EmailService.send_mentor_approval_email(mentor.user.email, mentor.user.full_name, approved=True)
        return mentor

    async def reject_mentor(self, mentor_id: int, admin: User, rejection_reason: str) -> Mentor:
        mentor = self.get_mentor_or_404(mentor_id)
        if mentor.approval_status == MentorApprovalStatus.APPROVED:
            raise ConflictException("Cannot reject a mentor that is already approved. Block the account instead.")

        mentor.approval_status = MentorApprovalStatus.REJECTED
        mentor.rejection_reason = sanitize_text(rejection_reason)
        self.db.add(mentor)
        self.db.commit()
        self.db.refresh(mentor)

        self.notification_service.notify(
            mentor.user_id, NotificationType.ACCOUNT, "Your mentor application was not approved",
            body=rejection_reason, reference_id=mentor.id,
        )
        self.audit_service.log(
            AuditAction.REJECT, actor_user_id=admin.id, entity_type="Mentor",
            entity_id=mentor.id, description=f"Mentor rejected: {rejection_reason}",
        )
        await EmailService.send_mentor_approval_email(
            mentor.user.email, mentor.user.full_name, approved=False, reason=rejection_reason
        )
        return mentor

    def review_document(
        self, document_id: int, admin: User, status: DocumentStatus, rejection_reason: Optional[str] = None
    ):
        document = self.document_repo.get(document_id)
        if document is None:
            raise NotFoundException("Document not found.")

        document.status = status
        document.reviewed_by_admin_id = admin.id
        document.reviewed_at = datetime.utcnow()
        document.rejection_reason = sanitize_text(rejection_reason) if status == DocumentStatus.REJECTED else None
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        return document
