"""
app/models/mentor.py
---------------------
Mentor profile - extends User 1:1. Holds professional data: qualifications,
achievements, expertise (linked via mentor_fields), approval workflow status,
and pricing/availability metadata used by students for search & filtering.
"""

from sqlalchemy import (
    Column, Integer, String, Float, Boolean, Text, ForeignKey, Enum as SAEnum, DateTime
)
from sqlalchemy.orm import relationship

from app.db.base_class import Base, TimestampMixin
from app.models.enums import MentorApprovalStatus
from app.models.category import mentor_fields


class Mentor(Base, TimestampMixin):
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)

    headline = Column(String(200), nullable=True)          # e.g. "Senior Data Scientist at XYZ"
    bio = Column(Text, nullable=True)
    years_of_experience = Column(Integer, default=0, nullable=False)
    current_organization = Column(String(200), nullable=True)
    designation = Column(String(150), nullable=True)

    # Stored as JSON-style text fields for flexibility; structured via Pydantic at the API layer.
    qualifications = Column(Text, nullable=True)   # JSON list: [{"degree":..,"institute":..,"year":..}]
    achievements = Column(Text, nullable=True)      # JSON list: [{"title":..,"description":..,"year":..}]

    hourly_rate = Column(Float, default=0.0, nullable=False)
    city = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)

    linkedin_url = Column(String(500), nullable=True)
    portfolio_url = Column(String(500), nullable=True)

    # ---------------- Admin approval workflow ----------------
    approval_status = Column(SAEnum(MentorApprovalStatus), default=MentorApprovalStatus.PENDING,
                              nullable=False, index=True)
    approved_by_admin_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    rejection_reason = Column(String(500), nullable=True)

    # Aggregate rating fields, denormalized for fast search/sort (recomputed on new rating)
    average_rating = Column(Float, default=0.0, nullable=False)
    total_ratings = Column(Integer, default=0, nullable=False)
    total_sessions_completed = Column(Integer, default=0, nullable=False)

    is_accepting_requests = Column(Boolean, default=True, nullable=False)

    # ---------------- Relationships ----------------
    user = relationship("User", back_populates="mentor_profile", foreign_keys=[user_id])
    documents = relationship("MentorDocument", back_populates="mentor", cascade="all, delete-orphan")
    availability_slots = relationship("MentorAvailabilitySlot", back_populates="mentor", cascade="all, delete-orphan")
    mentorship_requests = relationship("MentorshipRequest", back_populates="mentor", cascade="all, delete-orphan")
    bookings = relationship("Booking", back_populates="mentor", cascade="all, delete-orphan")
    ratings_received = relationship("Rating", back_populates="mentor", cascade="all, delete-orphan")
    expertise_fields = relationship("Field", secondary=mentor_fields, back_populates="mentors")

    def __repr__(self) -> str:
        return f"<Mentor id={self.id} user_id={self.user_id} status={self.approval_status}>"
