"""
app/schemas/chat.py
----------------------
Schemas for chat threads and messages between students and mentors.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import MessageType


class MessageCreateRequest(BaseModel):
    """Text message creation. For image/file messages, use the file upload endpoint instead."""
    content: str = Field(..., min_length=1, max_length=5000)


class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    chat_id: int
    sender_id: int
    message_type: MessageType
    content: Optional[str] = None
    attachment_path: Optional[str] = None
    is_read: bool
    created_at: datetime


class ChatOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    mentorship_request_id: int
    is_active: bool
    last_message_at: Optional[datetime] = None
    created_at: datetime


class ChatWithMessages(BaseModel):
    chat: ChatOut
    messages: List[MessageOut]
