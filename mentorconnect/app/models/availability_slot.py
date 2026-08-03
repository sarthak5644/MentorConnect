"""
app/models/availability_slot.py
---------------------------------
Time slots a mentor opens up for booking. Students book against a specific slot,
which then flips to BOOKED status (no double-booking thanks to a unique constraint
enforced at the service layer + DB-level status check).
"""

from sqlalchemy import Column, Integer, DateTime, ForeignKey, Enum as SAEnum, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db.base_class import Base, TimestampMixin
from app.models.enums import SlotStatus


class MentorAvailabilitySlot(Base, TimestampMixin):
    id = Column(Integer, primary_key=True, index=True)
    mentor_id = Column(Integer, ForeignKey("mentors.id", ondelete="CASCADE"), nullable=False, index=True)

    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=False)

    status = Column(SAEnum(SlotStatus), default=SlotStatus.AVAILABLE, nullable=False, index=True)

    mentor = relationship("Mentor", back_populates="availability_slots")
    booking = relationship("Booking", back_populates="slot", uselist=False)

    __table_args__ = (
        # A mentor cannot create two identical slots starting at the same time.
        UniqueConstraint("mentor_id", "start_time", name="uq_mentor_slot_start"),
    )

    def __repr__(self) -> str:
        return f"<MentorAvailabilitySlot id={self.id} mentor_id={self.mentor_id} start={self.start_time}>"
