"""
app/schemas/complaint.py
---------------------------
Schemas for students filing complaints and admins resolving them.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import ComplaintStatus


class ComplaintCreateRequest(BaseModel):
    against_user_id: Optional[int] = None
    booking_id: Optional[int] = None
    subject: str = Field(..., min_length=5, max_length=200)
    description: str = Field(..., min_length=10, max_length=3000)


class ComplaintResolveRequest(BaseModel):
    status: ComplaintStatus = Field(..., description="'resolved' or 'dismissed'")
    admin_notes: Optional[str] = Field(None, max_length=2000)


class ComplaintOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    student_id: int
    against_user_id: Optional[int] = None
    booking_id: Optional[int] = None
    subject: str
    description: str
    status: ComplaintStatus
    admin_notes: Optional[str] = None
    resolved_at: Optional[datetime] = None
    created_at: datetime
