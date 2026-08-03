"""
app/repositories/otp_repository.py
----------------------------------------
Data access methods for OTP verification records.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.otp_verification import OtpVerification
from app.models.enums import OtpPurpose
from app.repositories.base import BaseRepository


class OtpRepository(BaseRepository[OtpVerification]):
    def __init__(self, db: Session):
        super().__init__(OtpVerification, db)

    def get_latest_active(self, destination: str, purpose: OtpPurpose) -> Optional[OtpVerification]:
        """Get the most recent, unused, non-expired OTP for a destination + purpose."""
        stmt = (
            select(OtpVerification)
            .where(
                OtpVerification.destination == destination,
                OtpVerification.purpose == purpose,
                OtpVerification.is_used == False,  # noqa: E712
                OtpVerification.expires_at > datetime.utcnow(),
            )
            .order_by(OtpVerification.created_at.desc())
        )
        return self.db.execute(stmt).scalars().first()

    def get_most_recent(self, destination: str, purpose: OtpPurpose) -> Optional[OtpVerification]:
        """Get the most recent OTP regardless of used/expired state (for resend cooldown checks)."""
        stmt = (
            select(OtpVerification)
            .where(OtpVerification.destination == destination, OtpVerification.purpose == purpose)
            .order_by(OtpVerification.created_at.desc())
        )
        return self.db.execute(stmt).scalars().first()
