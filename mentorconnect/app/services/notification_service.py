"""
app/services/notification_service.py
----------------------------------------
Creates in-app notifications for users (mentorship request updates, booking
events, chat messages, system/admin announcements). This is the single place
that writes to the `notifications` table, so the shape stays consistent
no matter which feature triggers it.
"""

from typing import Optional, List
from sqlalchemy.orm import Session

from app.models.enums import NotificationType
from app.repositories.notification_repository import NotificationRepository


class NotificationService:
    def __init__(self, db: Session):
        self.repo = NotificationRepository(db)

    def notify(
        self,
        user_id: int,
        notif_type: NotificationType,
        title: str,
        body: Optional[str] = None,
        reference_id: Optional[int] = None,
    ) -> None:
        """Create a single notification for one user."""
        self.repo.create({
            "user_id": user_id,
            "type": notif_type,
            "title": title,
            "body": body,
            "reference_id": reference_id,
            "is_read": False,
        })

    def notify_many(
        self,
        user_ids: List[int],
        notif_type: NotificationType,
        title: str,
        body: Optional[str] = None,
        reference_id: Optional[int] = None,
    ) -> None:
        """Create the same notification for multiple users (e.g. broadcast/system announcement)."""
        for uid in user_ids:
            self.notify(uid, notif_type, title, body, reference_id)

    def list_for_user(self, user_id: int, skip: int = 0, limit: int = 20):
        return self.repo.list_by_user(user_id, skip, limit)

    def unread_count(self, user_id: int) -> int:
        return self.repo.count_unread(user_id)

    def mark_read(self, user_id: int, notification_ids: List[int]) -> None:
        self.repo.mark_read(user_id, notification_ids)
