"""
app/schemas/rating.py
------------------------
Schemas for students rating mentors after a completed booking.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class RatingCreateRequest(BaseModel):
    booking_id: int
    score: int = Field(..., ge=1, le=5)
    review: Optional[str] = Field(None, max_length=2000)


class RatingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    booking_id: int
    student_id: int
    mentor_id: int
    score: int
    review: Optional[str] = None
    created_at: datetime
