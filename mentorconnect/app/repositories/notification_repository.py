"""
app/repositories/notification_repository.py
--------------------------------------------------
Data access methods for in-app notifications.
"""

from typing import List
from sqlalchemy import select, func, update
from sqlalchemy.orm import Session

from app.models.notification import Notification
from app.repositories.base import BaseRepository


class NotificationRepository(BaseRepository[Notification]):
    def __init__(self, db: Session):
        super().__init__(Notification, db)

    def list_by_user(self, user_id: int, skip: int = 0, limit: int = 20) -> List[Notification]:
        stmt = (
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
            .offset(skip).limit(limit)
        )
        return list(self.db.execute(stmt).scalars().all())

    def count_unread(self, user_id: int) -> int:
        stmt = select(func.count()).select_from(Notification).where(
            Notification.user_id == user_id, Notification.is_read == False  # noqa: E712
        )
        return self.db.execute(stmt).scalar_one()

    def mark_read(self, user_id: int, notification_ids: List[int]) -> None:
        from datetime import datetime
        stmt = (
            update(Notification)
            .where(Notification.user_id == user_id, Notification.id.in_(notification_ids))
            .values(is_read=True, read_at=datetime.utcnow())
        )
        self.db.execute(stmt)
        self.db.commit()
