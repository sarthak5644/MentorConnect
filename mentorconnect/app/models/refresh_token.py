"""
app/models/refresh_token.py
------------------------------
Tracks issued refresh tokens server-side so individual sessions can be revoked
(e.g. "logout this device", "logout everywhere"), and so a stolen/leaked refresh
token can be invalidated without rotating every user's secret.
Not in the original table list but required for production-safe JWT refresh flows.
"""

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.db.base_class import Base, TimestampMixin


class RefreshToken(Base, TimestampMixin):
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # We store a hash of the token (never the raw token) so a DB leak doesn't leak usable tokens.
    token_hash = Column(String(255), unique=True, nullable=False, index=True)

    is_revoked = Column(Boolean, default=False, nullable=False)
    expires_at = Column(DateTime, nullable=False, index=True)

    user_agent = Column(String(255), nullable=True)
    ip_address = Column(String(64), nullable=True)

    user = relationship("User")

    def __repr__(self) -> str:
        return f"<RefreshToken id={self.id} user_id={self.user_id} revoked={self.is_revoked}>"
