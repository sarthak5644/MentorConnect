"""
app/models/audit_log.py
--------------------------
Immutable audit trail of significant actions across the platform: logins,
admin approvals/rejections, blocks, data changes. Written by
services/audit_service.py - never updated or deleted, only inserted.
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship

from app.db.base_class import Base, TimestampMixin
from app.models.enums import AuditAction


class AuditLog(Base, TimestampMixin):
    id = Column(Integer, primary_key=True, index=True)

    actor_user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)  # null = system action
    action = Column(SAEnum(AuditAction), nullable=False, index=True)

    entity_type = Column(String(100), nullable=True, index=True)   # e.g. "Mentor", "User", "Booking"
    entity_id = Column(Integer, nullable=True, index=True)

    description = Column(Text, nullable=True)
    ip_address = Column(String(64), nullable=True)
    user_agent = Column(String(255), nullable=True)

    actor = relationship("User", back_populates="audit_logs", foreign_keys=[actor_user_id])

    def __repr__(self) -> str:
        return f"<AuditLog id={self.id} action={self.action} entity_type={self.entity_type}>"
