"""
app/models/student.py
----------------------
Student profile - extends User 1:1. Holds education/interest data
used for search/filtering and personalization (not auth data, that's on User).
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import relationship

from app.db.base_class import Base, TimestampMixin


class Student(Base, TimestampMixin):
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)

    institution_name = Column(String(200), nullable=True)
    education_level = Column(String(100), nullable=True)   # e.g. "Undergraduate", "High School"
    field_of_study = Column(String(150), nullable=True)
    date_of_birth = Column(Date, nullable=True)
    bio = Column(String(1000), nullable=True)
    city = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    interests = Column(String(500), nullable=True)  # comma-separated tags for quick personalization

    # ---------------- Relationships ----------------
    user = relationship("User", back_populates="student_profile")
    mentorship_requests = relationship("MentorshipRequest", back_populates="student", cascade="all, delete-orphan")
    bookings = relationship("Booking", back_populates="student", cascade="all, delete-orphan")
    ratings_given = relationship("Rating", back_populates="student", cascade="all, delete-orphan")
    complaints_filed = relationship("Complaint", back_populates="student", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Student id={self.id} user_id={self.user_id}>"
