"""
app/schemas/mentor.py
------------------------
Schemas for the Mentor profile entity: profile updates, qualifications,
achievements, expertise fields, and the admin approval workflow.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from app.models.enums import MentorApprovalStatus
from app.schemas.user import UserOut


class QualificationItem(BaseModel):
    """A single qualification entry, stored as JSON inside Mentor.qualifications."""
    degree: str = Field(..., max_length=150)
    institute: str = Field(..., max_length=200)
    year: int = Field(..., ge=1950, le=2100)


class AchievementItem(BaseModel):
    """A single achievement entry, stored as JSON inside Mentor.achievements."""
    title: str = Field(..., max_length=200)
    description: Optional[str] = Field(None, max_length=500)
    year: Optional[int] = Field(None, ge=1950, le=2100)


class MentorProfileUpdate(BaseModel):
    headline: Optional[str] = Field(None, max_length=200)
    bio: Optional[str] = Field(None, max_length=3000)
    years_of_experience: Optional[int] = Field(None, ge=0, le=80)
    current_organization: Optional[str] = Field(None, max_length=200)
    designation: Optional[str] = Field(None, max_length=150)
    hourly_rate: Optional[float] = Field(None, ge=0)
    city: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    linkedin_url: Optional[HttpUrl] = None
    portfolio_url: Optional[HttpUrl] = None
    is_accepting_requests: Optional[bool] = None


class MentorQualificationsUpdate(BaseModel):
    qualifications: List[QualificationItem]


class MentorAchievementsUpdate(BaseModel):
    achievements: List[AchievementItem]


class MentorExpertiseUpdate(BaseModel):
    field_ids: List[int] = Field(..., description="List of Field IDs representing the mentor's expertise")


class FieldOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    category_id: int


class MentorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    headline: Optional[str] = None
    bio: Optional[str] = None
    years_of_experience: int
    current_organization: Optional[str] = None
    designation: Optional[str] = None
    qualifications: Optional[str] = None
    achievements: Optional[str] = None
    hourly_rate: float
    city: Optional[str] = None
    country: Optional[str] = None
    linkedin_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    approval_status: MentorApprovalStatus
    average_rating: float
    total_ratings: int
    total_sessions_completed: int
    is_accepting_requests: bool
    expertise_fields: List[FieldOut] = []
    created_at: datetime


class MentorProfileResponse(BaseModel):
    """Combined view: account info (User) + mentor-specific profile data."""
    user: UserOut
    profile: MentorOut


class MentorPublicCard(BaseModel):
    """
    Lightweight mentor representation for search/listing results -
    avoids leaking internal/sensitive fields and keeps payload small.
    """
    model_config = ConfigDict(from_attributes=True)

    id: int
    headline: Optional[str] = None
    years_of_experience: int
    current_organization: Optional[str] = None
    designation: Optional[str] = None
    hourly_rate: float
    city: Optional[str] = None
    country: Optional[str] = None
    average_rating: float
    total_ratings: int
    is_accepting_requests: bool
    expertise_fields: List[FieldOut] = []


class MentorSearchFilters(BaseModel):
    """Query parameters for mentor search/filter endpoint."""
    keyword: Optional[str] = Field(None, max_length=150, description="Search in name/headline/bio")
    field_id: Optional[int] = None
    category_id: Optional[int] = None
    min_rating: Optional[float] = Field(None, ge=0, le=5)
    max_hourly_rate: Optional[float] = Field(None, ge=0)
    min_experience: Optional[int] = Field(None, ge=0)
    city: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    is_accepting_requests: Optional[bool] = None


class MentorApprovalRequest(BaseModel):
    """Admin action: approve a mentor."""
    notes: Optional[str] = Field(None, max_length=500)


class MentorRejectionRequest(BaseModel):
    """Admin action: reject a mentor, with a required reason."""
    rejection_reason: str = Field(..., min_length=5, max_length=500)
