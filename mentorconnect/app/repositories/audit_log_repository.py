"""
app/repositories/audit_log_repository.py
-----------------------------------------------
Data access methods for the audit trail.
"""

from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.models.enums import AuditAction
from app.repositories.base import BaseRepository


class AuditLogRepository(BaseRepository[AuditLog]):
    def __init__(self, db: Session):
        super().__init__(AuditLog, db)

    def list_all(
        self, action: Optional[AuditAction] = None, entity_type: Optional[str] = None,
        skip: int = 0, limit: int = 50
    ) -> List[AuditLog]:
        stmt = select(AuditLog)
        if action is not None:
            stmt = stmt.where(AuditLog.action == action)
        if entity_type is not None:
            stmt = stmt.where(AuditLog.entity_type == entity_type)
        stmt = stmt.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit)
        return list(self.db.execute(stmt).scalars().all())
