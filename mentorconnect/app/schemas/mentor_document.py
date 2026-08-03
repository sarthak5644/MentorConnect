"""
app/schemas/mentor_document.py
---------------------------------
Schemas for mentor document upload & admin review workflow.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import DocumentStatus


class MentorDocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    mentor_id: int
    document_type: str
    file_name: str
    file_size_bytes: Optional[int] = None
    mime_type: Optional[str] = None
    status: DocumentStatus
    rejection_reason: Optional[str] = None
    created_at: datetime


class MentorDocumentReviewRequest(BaseModel):
    status: DocumentStatus = Field(..., description="Set to 'verified' or 'rejected'")
    rejection_reason: Optional[str] = Field(None, max_length=500)
