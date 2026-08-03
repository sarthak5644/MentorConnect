"""
app/models/captcha_session.py
--------------------------------
Image captcha challenge sessions. A captcha is generated server-side (random text
rendered into a distorted PNG), the answer is hashed and stored here keyed by a
session_id (UUID) that the client must echo back along with their answer on
sensitive actions (registration, login, OTP request) to prove they're not a bot.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime

from app.db.base_class import Base, TimestampMixin


class CaptchaSession(Base, TimestampMixin):
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(64), unique=True, nullable=False, index=True)   # UUID4 given to client

    hashed_answer = Column(String(255), nullable=False)
    is_used = Column(Boolean, default=False, nullable=False)
    expires_at = Column(DateTime, nullable=False, index=True)

    def __repr__(self) -> str:
        return f"<CaptchaSession id={self.id} session_id={self.session_id}>"
