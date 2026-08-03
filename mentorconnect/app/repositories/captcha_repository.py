"""
app/repositories/captcha_repository.py
---------------------------------------------
Data access methods for image captcha sessions.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.captcha_session import CaptchaSession
from app.repositories.base import BaseRepository


class CaptchaRepository(BaseRepository[CaptchaSession]):
    def __init__(self, db: Session):
        super().__init__(CaptchaSession, db)

    def get_active_by_session_id(self, session_id: str) -> Optional[CaptchaSession]:
        stmt = select(CaptchaSession).where(
            CaptchaSession.session_id == session_id,
            CaptchaSession.is_used == False,  # noqa: E712
            CaptchaSession.expires_at > datetime.utcnow(),
        )
        return self.db.execute(stmt).scalar_one_or_none()
