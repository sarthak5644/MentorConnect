"""
app/schemas/notification.py
-------------------------------
Schemas for in-app notifications.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

from app.models.enums import NotificationType


class NotificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    type: NotificationType
    title: str
    body: Optional[str] = None
    reference_id: Optional[int] = None
    is_read: bool
    created_at: datetime


class NotificationMarkReadRequest(BaseModel):
    notification_ids: list[int]
