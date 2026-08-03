"""
app/models/notification.py
----------------------------
In-app notifications delivered to a user (mentorship request updates, booking
reminders, chat messages, system/admin announcements). Powers the notification
bell/list in the frontend; created by services/notification_service.py.
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, Enum as SAEnum, DateTime
from sqlalchemy.orm import relationship

from app.db.base_class import Base, TimestampMixin
from app.models.enums import NotificationType


class Notification(Base, TimestampMixin):
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    type = Column(SAEnum(NotificationType), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    body = Column(Text, nullable=True)
    reference_id = Column(Integer, nullable=True)   # generic FK to related entity (booking id, request id, etc.)

    is_read = Column(Boolean, default=False, nullable=False, index=True)
    read_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="notifications")

    def __repr__(self) -> str:
        return f"<Notification id={self.id} user_id={self.user_id} type={self.type}>"
