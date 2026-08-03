"""
app/models/chat.py
--------------------
Chat is the 1:1 conversation thread tied to an accepted MentorshipRequest.
Message is each individual text/image/file message inside a Chat.
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, Enum as SAEnum, DateTime
from sqlalchemy.orm import relationship

from app.db.base_class import Base, TimestampMixin
from app.models.enums import MessageType


class Chat(Base, TimestampMixin):
    id = Column(Integer, primary_key=True, index=True)
    mentorship_request_id = Column(
        Integer, ForeignKey("mentorship_requests.id", ondelete="CASCADE"),
        unique=True, nullable=False, index=True
    )
    is_active = Column(Boolean, default=True, nullable=False)
    last_message_at = Column(DateTime, nullable=True)

    mentorship_request = relationship("MentorshipRequest", back_populates="chat")
    messages = relationship("Message", back_populates="chat", cascade="all, delete-orphan",
                             order_by="Message.created_at")

    def __repr__(self) -> str:
        return f"<Chat id={self.id} mentorship_request_id={self.mentorship_request_id}>"


class Message(Base, TimestampMixin):
    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("chats.id", ondelete="CASCADE"), nullable=False, index=True)
    sender_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    message_type = Column(SAEnum(MessageType), default=MessageType.TEXT, nullable=False)
    content = Column(Text, nullable=True)          # text content (sanitized, see utils/sanitizer.py)
    attachment_path = Column(String(500), nullable=True)   # for image/file messages

    is_read = Column(Boolean, default=False, nullable=False)
    read_at = Column(DateTime, nullable=True)

    chat = relationship("Chat", back_populates="messages")
    sender = relationship("User")

    def __repr__(self) -> str:
        return f"<Message id={self.id} chat_id={self.chat_id} sender_id={self.sender_id}>"
