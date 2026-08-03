"""
app/services/audit_service.py
---------------------------------
Writes immutable audit trail entries for significant actions (logins, admin
approvals/rejections, blocks, data changes). Called from services/routers
whenever a security or business-significant event occurs.
"""

from typing import Optional
from sqlalchemy.orm import Session
from fastapi import Request

from app.models.enums import AuditAction
from app.repositories.audit_log_repository import AuditLogRepository


class AuditService:
    def __init__(self, db: Session):
        self.repo = AuditLogRepository(db)

    def log(
        self,
        action: AuditAction,
        actor_user_id: Optional[int] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[int] = None,
        description: Optional[str] = None,
        request: Optional[Request] = None,
    ) -> None:
        """
        Records an audit log entry. Accepts an optional FastAPI Request to
        automatically capture IP address and user agent for forensic purposes.
        """
        ip_address = None
        user_agent = None
        if request is not None:
            ip_address = request.client.host if request.client else None
            user_agent = request.headers.get("user-agent")

        self.repo.create({
            "actor_user_id": actor_user_id,
            "action": action,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "description": description,
            "ip_address": ip_address,
            "user_agent": user_agent,
        })
