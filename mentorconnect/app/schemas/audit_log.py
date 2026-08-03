"""
app/schemas/audit_log.py
----------------------------
Schemas for reading audit log entries (admin-only endpoint).
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

from app.models.enums import AuditAction


class AuditLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    actor_user_id: Optional[int] = None
    action: AuditAction
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    description: Optional[str] = None
    ip_address: Optional[str] = None
    created_at: datetime
