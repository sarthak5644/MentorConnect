"""
app/repositories/booking_repository.py
---------------------------------------------
Data access methods for bookings.
"""

from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models.booking import Booking
from app.models.enums import BookingStatus
from app.repositories.base import BaseRepository


class BookingRepository(BaseRepository[Booking]):
    def __init__(self, db: Session):
        super().__init__(Booking, db)

    def get_by_slot_id(self, slot_id: int) -> Optional[Booking]:
        stmt = select(Booking).where(Booking.slot_id == slot_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def list_by_student(self, student_id: int, skip: int = 0, limit: int = 20) -> List[Booking]:
        stmt = (
            select(Booking)
            .where(Booking.student_id == student_id)
            .order_by(Booking.created_at.desc())
            .offset(skip).limit(limit)
        )
        return list(self.db.execute(stmt).scalars().all())

    def list_by_mentor(
        self, mentor_id: int, status: Optional[BookingStatus] = None,
        skip: int = 0, limit: int = 20
    ) -> List[Booking]:
        stmt = select(Booking).where(Booking.mentor_id == mentor_id)
        if status is not None:
            stmt = stmt.where(Booking.status == status)
        stmt = stmt.order_by(Booking.created_at.desc()).offset(skip).limit(limit)
        return list(self.db.execute(stmt).scalars().all())

    def count_all(self) -> int:
        stmt = select(func.count()).select_from(Booking)
        return self.db.execute(stmt).scalar_one()

    def count_by_status(self, status: BookingStatus) -> int:
        stmt = select(func.count()).select_from(Booking).where(Booking.status == status)
        return self.db.execute(stmt).scalar_one()

    def count_grouped_by_status(self) -> dict:
        stmt = select(Booking.status, func.count()).group_by(Booking.status)
        rows = self.db.execute(stmt).all()
        return {status.value: count for status, count in rows}
