"""
app/schemas/student.py
-------------------------
Schemas for the Student profile entity (separate from User auth schema).
"""

from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from app.schemas.user import UserOut


class StudentProfileUpdate(BaseModel):
    institution_name: Optional[str] = Field(None, max_length=200)
    education_level: Optional[str] = Field(None, max_length=100)
    field_of_study: Optional[str] = Field(None, max_length=150)
    date_of_birth: Optional[date] = None
    bio: Optional[str] = Field(None, max_length=1000)
    city: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    interests: Optional[str] = Field(None, max_length=500)


class StudentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    institution_name: Optional[str] = None
    education_level: Optional[str] = None
    field_of_study: Optional[str] = None
    date_of_birth: Optional[date] = None
    bio: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    interests: Optional[str] = None
    created_at: datetime


class StudentProfileResponse(BaseModel):
    """Combined view: account info (User) + student-specific profile data."""
    user: UserOut
    profile: StudentOut
