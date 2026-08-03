"""
app/repositories/complaint_repository.py
-----------------------------------------------
Data access methods for complaints.
"""

from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models.complaint import Complaint
from app.models.enums import ComplaintStatus
from app.repositories.base import BaseRepository


class ComplaintRepository(BaseRepository[Complaint]):
    def __init__(self, db: Session):
        super().__init__(Complaint, db)

    def list_by_student(self, student_id: int, skip: int = 0, limit: int = 20) -> List[Complaint]:
        stmt = (
            select(Complaint)
            .where(Complaint.student_id == student_id)
            .order_by(Complaint.created_at.desc())
            .offset(skip).limit(limit)
        )
        return list(self.db.execute(stmt).scalars().all())

    def list_all(self, status: Optional[ComplaintStatus] = None, skip: int = 0, limit: int = 20) -> List[Complaint]:
        stmt = select(Complaint)
        if status is not None:
            stmt = stmt.where(Complaint.status == status)
        stmt = stmt.order_by(Complaint.created_at.desc()).offset(skip).limit(limit)
        return list(self.db.execute(stmt).scalars().all())

    def count_by_status(self, status: ComplaintStatus) -> int:
        stmt = select(func.count()).select_from(Complaint).where(Complaint.status == status)
        return self.db.execute(stmt).scalar_one()

    def count_grouped_by_status(self) -> dict:
        stmt = select(Complaint.status, func.count()).group_by(Complaint.status)
        rows = self.db.execute(stmt).all()
        return {status.value: count for status, count in rows}
