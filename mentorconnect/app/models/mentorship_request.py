"""
app/models/mentorship_request.py
-----------------------------------
A student's request to a mentor to begin a mentorship relationship.
Mentor can accept/reject. Once accepted, the student can book slots and chat.
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum as SAEnum, DateTime
from sqlalchemy.orm import relationship

from app.db.base_class import Base, TimestampMixin
from app.models.enums import MentorshipRequestStatus


class MentorshipRequest(Base, TimestampMixin):
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    mentor_id = Column(Integer, ForeignKey("mentors.id", ondelete="CASCADE"), nullable=False, index=True)

    message = Column(Text, nullable=True)   # student's intro message / goal statement
    status = Column(SAEnum(MentorshipRequestStatus), default=MentorshipRequestStatus.PENDING,
                     nullable=False, index=True)

    responded_at = Column(DateTime, nullable=True)
    response_note = Column(String(500), nullable=True)   # mentor's reason for accept/reject

    student = relationship("Student", back_populates="mentorship_requests")
    mentor = relationship("Mentor", back_populates="mentorship_requests")
    chat = relationship("Chat", back_populates="mentorship_request", uselist=False, cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<MentorshipRequest id={self.id} student_id={self.student_id} mentor_id={self.mentor_id}>"
