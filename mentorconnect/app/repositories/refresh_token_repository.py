"""
app/repositories/refresh_token_repository.py
---------------------------------------------------
Data access methods for tracking issued refresh tokens (for revocation/logout).
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models.refresh_token import RefreshToken
from app.repositories.base import BaseRepository


class RefreshTokenRepository(BaseRepository[RefreshToken]):
    def __init__(self, db: Session):
        super().__init__(RefreshToken, db)

    def get_active_by_hash(self, token_hash: str) -> Optional[RefreshToken]:
        stmt = select(RefreshToken).where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.is_revoked == False,  # noqa: E712
            RefreshToken.expires_at > datetime.utcnow(),
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def revoke(self, token_hash: str) -> None:
        stmt = update(RefreshToken).where(RefreshToken.token_hash == token_hash).values(is_revoked=True)
        self.db.execute(stmt)
        self.db.commit()

    def revoke_all_for_user(self, user_id: int) -> None:
        stmt = update(RefreshToken).where(RefreshToken.user_id == user_id).values(is_revoked=True)
        self.db.execute(stmt)
        self.db.commit()
