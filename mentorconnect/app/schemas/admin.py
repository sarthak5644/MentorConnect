"""
app/schemas/admin.py
------------------------
Schemas for Super Admin user-management actions: blocking/unblocking accounts.
"""

from typing import Optional
from pydantic import BaseModel, Field

from app.models.enums import UserStatus


class BlockUserRequest(BaseModel):
    reason: str = Field(..., min_length=3, max_length=255)


class UserStatusUpdateRequest(BaseModel):
    status: UserStatus
    reason: Optional[str] = Field(None, max_length=255)
