"""
app/models/complaint.py
-------------------------
Complaints filed by students against mentors (or vice versa, via against_user_id)
for the Super Admin to review and resolve. Supports the admin moderation workflow.
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum as SAEnum, DateTime
from sqlalchemy.orm import relationship

from app.db.base_class import Base, TimestampMixin
from app.models.enums import ComplaintStatus


class Complaint(Base, TimestampMixin):
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)

    against_user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=True)

    subject = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)

    status = Column(SAEnum(ComplaintStatus), default=ComplaintStatus.OPEN, nullable=False, index=True)
    admin_notes = Column(Text, nullable=True)
    resolved_by_admin_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    resolved_at = Column(DateTime, nullable=True)

    student = relationship("Student", back_populates="complaints_filed")
    against_user = relationship("User", foreign_keys=[against_user_id])

    def __repr__(self) -> str:
        return f"<Complaint id={self.id} student_id={self.student_id} status={self.status}>"
