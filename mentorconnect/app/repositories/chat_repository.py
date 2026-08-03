"""
app/repositories/chat_repository.py
----------------------------------------
Data access methods for chat threads and messages.
"""

from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.chat import Chat, Message
from app.repositories.base import BaseRepository


class ChatRepository(BaseRepository[Chat]):
    def __init__(self, db: Session):
        super().__init__(Chat, db)

    def get_by_mentorship_request(self, mentorship_request_id: int) -> Optional[Chat]:
        stmt = select(Chat).where(Chat.mentorship_request_id == mentorship_request_id)
        return self.db.execute(stmt).scalar_one_or_none()


class MessageRepository(BaseRepository[Message]):
    def __init__(self, db: Session):
        super().__init__(Message, db)

    def list_by_chat(self, chat_id: int, skip: int = 0, limit: int = 50) -> List[Message]:
        stmt = (
            select(Message)
            .where(Message.chat_id == chat_id)
            .order_by(Message.created_at.asc())
            .offset(skip).limit(limit)
        )
        return list(self.db.execute(stmt).scalars().all())

    def mark_all_read(self, chat_id: int, reader_user_id: int) -> None:
        """Mark all messages in a chat as read, except those sent by the reader themself."""
        from datetime import datetime
        stmt = select(Message).where(
            Message.chat_id == chat_id,
            Message.sender_id != reader_user_id,
            Message.is_read == False,  # noqa: E712 - SQLAlchemy requires == for column comparison
        )
        messages = self.db.execute(stmt).scalars().all()
        now = datetime.utcnow()
        for msg in messages:
            msg.is_read = True
            msg.read_at = now
        self.db.commit()
