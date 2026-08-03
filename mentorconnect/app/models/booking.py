"""
app/models/booking.py
-----------------------
A confirmed booking of a mentor's availability slot by a student.
One-to-one with MentorAvailabilitySlot (a slot, once booked, can't be reused).
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum as SAEnum, DateTime
from sqlalchemy.orm import relationship

from app.db.base_class import Base, TimestampMixin
from app.models.enums import BookingStatus


class Booking(Base, TimestampMixin):
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    mentor_id = Column(Integer, ForeignKey("mentors.id", ondelete="CASCADE"), nullable=False, index=True)
    slot_id = Column(Integer, ForeignKey("mentor_availability_slots.id", ondelete="CASCADE"),
                      unique=True, nullable=False, index=True)

    status = Column(SAEnum(BookingStatus), default=BookingStatus.SCHEDULED, nullable=False, index=True)
    meeting_link = Column(String(500), nullable=True)   # e.g. video call URL generated on confirmation
    notes = Column(Text, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)
    cancellation_reason = Column(String(500), nullable=True)

    student = relationship("Student", back_populates="bookings")
    mentor = relationship("Mentor", back_populates="bookings")
    slot = relationship("MentorAvailabilitySlot", back_populates="booking")
    rating = relationship("Rating", back_populates="booking", uselist=False, cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Booking id={self.id} student_id={self.student_id} mentor_id={self.mentor_id}>"
