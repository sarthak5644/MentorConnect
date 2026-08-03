"""
app/repositories/slot_repository.py
----------------------------------------
Data access methods for mentor availability slots.
"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.availability_slot import MentorAvailabilitySlot
from app.models.enums import SlotStatus
from app.repositories.base import BaseRepository


class SlotRepository(BaseRepository[MentorAvailabilitySlot]):
    def __init__(self, db: Session):
        super().__init__(MentorAvailabilitySlot, db)

    def list_by_mentor(
        self, mentor_id: int, status: Optional[SlotStatus] = None,
        from_time: Optional[datetime] = None
    ) -> List[MentorAvailabilitySlot]:
        stmt = select(MentorAvailabilitySlot).where(MentorAvailabilitySlot.mentor_id == mentor_id)
        if status is not None:
            stmt = stmt.where(MentorAvailabilitySlot.status == status)
        if from_time is not None:
            stmt = stmt.where(MentorAvailabilitySlot.start_time >= from_time)
        stmt = stmt.order_by(MentorAvailabilitySlot.start_time.asc())
        return list(self.db.execute(stmt).scalars().all())

    def get_overlapping(
        self, mentor_id: int, start_time: datetime, end_time: datetime
    ) -> List[MentorAvailabilitySlot]:
        """Find any existing slots for this mentor that overlap the given time range."""
        stmt = select(MentorAvailabilitySlot).where(
            MentorAvailabilitySlot.mentor_id == mentor_id,
            MentorAvailabilitySlot.start_time < end_time,
            MentorAvailabilitySlot.end_time > start_time,
        )
        return list(self.db.execute(stmt).scalars().all())
