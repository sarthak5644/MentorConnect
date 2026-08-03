"""
app/repositories/mentorship_request_repository.py
-------------------------------------------------------
Data access methods for mentorship requests.
"""

from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models.mentorship_request import MentorshipRequest
from app.models.enums import MentorshipRequestStatus
from app.repositories.base import BaseRepository


class MentorshipRequestRepository(BaseRepository[MentorshipRequest]):
    def __init__(self, db: Session):
        super().__init__(MentorshipRequest, db)

    def get_pending_between(self, student_id: int, mentor_id: int) -> Optional[MentorshipRequest]:
        """Check if a student already has a pending request to this mentor (prevent duplicates)."""
        stmt = select(MentorshipRequest).where(
            MentorshipRequest.student_id == student_id,
            MentorshipRequest.mentor_id == mentor_id,
            MentorshipRequest.status == MentorshipRequestStatus.PENDING,
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def list_by_student(self, student_id: int, skip: int = 0, limit: int = 20) -> List[MentorshipRequest]:
        stmt = (
            select(MentorshipRequest)
            .where(MentorshipRequest.student_id == student_id)
            .order_by(MentorshipRequest.created_at.desc())
            .offset(skip).limit(limit)
        )
        return list(self.db.execute(stmt).scalars().all())

    def list_by_mentor(
        self, mentor_id: int, status: Optional[MentorshipRequestStatus] = None,
        skip: int = 0, limit: int = 20
    ) -> List[MentorshipRequest]:
        stmt = select(MentorshipRequest).where(MentorshipRequest.mentor_id == mentor_id)
        if status is not None:
            stmt = stmt.where(MentorshipRequest.status == status)
        stmt = stmt.order_by(MentorshipRequest.created_at.desc()).offset(skip).limit(limit)
        return list(self.db.execute(stmt).scalars().all())

    def count_all(self) -> int:
        stmt = select(func.count()).select_from(MentorshipRequest)
        return self.db.execute(stmt).scalar_one()
