"""
app/models/otp_verification.py
---------------------------------
Stores OTP codes issued for email verification, mobile verification,
password reset, or 2FA login. The raw OTP is hashed before storage
(never store plain OTP codes, same principle as passwords).
"""

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Enum as SAEnum, DateTime
from sqlalchemy.orm import relationship

from app.db.base_class import Base, TimestampMixin
from app.models.enums import OtpPurpose, OtpChannel


class OtpVerification(Base, TimestampMixin):
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)

    # Target contact info OTP was sent to (kept even if user_id is null, e.g. pre-registration OTP)
    destination = Column(String(150), nullable=False, index=True)   # email address or mobile number
    channel = Column(SAEnum(OtpChannel), nullable=False)
    purpose = Column(SAEnum(OtpPurpose), nullable=False, index=True)

    hashed_otp = Column(String(255), nullable=False)
    attempts = Column(Integer, default=0, nullable=False)
    is_used = Column(Boolean, default=False, nullable=False)
    expires_at = Column(DateTime, nullable=False, index=True)

    user = relationship("User", back_populates="otp_verifications")

    def __repr__(self) -> str:
        return f"<OtpVerification id={self.id} destination={self.destination} purpose={self.purpose}>"
