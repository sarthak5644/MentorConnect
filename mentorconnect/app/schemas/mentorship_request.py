"""
app/schemas/mentorship_request.py
-------------------------------------
Schemas for students sending mentorship requests and mentors accepting/rejecting them.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import MentorshipRequestStatus


class MentorshipRequestCreate(BaseModel):
    mentor_id: int
    message: Optional[str] = Field(None, max_length=2000)


class MentorshipRequestRespond(BaseModel):
    """Mentor's response: accept or reject."""
    status: MentorshipRequestStatus = Field(..., description="Must be 'accepted' or 'rejected'")
    response_note: Optional[str] = Field(None, max_length=500)


class MentorshipRequestOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    student_id: int
    mentor_id: int
    message: Optional[str] = None
    status: MentorshipRequestStatus
    response_note: Optional[str] = None
    responded_at: Optional[datetime] = None
    created_at: datetime
