"""
app/schemas/booking.py
-------------------------
Schemas for students booking mentor slots and managing bookings.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import BookingStatus


class BookingCreateRequest(BaseModel):
    slot_id: int
    notes: Optional[str] = Field(None, max_length=1000)


class BookingCancelRequest(BaseModel):
    cancellation_reason: str = Field(..., min_length=3, max_length=500)


class BookingStatusUpdateRequest(BaseModel):
    status: BookingStatus


class BookingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    student_id: int
    mentor_id: int
    slot_id: int
    status: BookingStatus
    meeting_link: Optional[str] = None
    notes: Optional[str] = None
    cancellation_reason: Optional[str] = None
    created_at: datetime
