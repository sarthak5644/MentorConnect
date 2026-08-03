"""
app/services/otp_service.py
-------------------------------
Generates, sends, and verifies OTP codes for email/mobile verification,
password reset, and 2FA. Enforces resend cooldowns and max-attempt lockouts
to prevent brute-forcing and SMS/email bombing abuse.
"""

from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import generate_secure_code, hash_token, constant_time_compare
from app.core.exceptions import OtpException, TooManyRequestsException
from app.models.enums import OtpPurpose, OtpChannel
from app.repositories.otp_repository import OtpRepository
from app.services.email_service import EmailService
from app.services.sms_service import SmsService

_PURPOSE_LABELS = {
    OtpPurpose.EMAIL_VERIFICATION: "email verification",
    OtpPurpose.MOBILE_VERIFICATION: "mobile verification",
    OtpPurpose.PASSWORD_RESET: "password reset",
    OtpPurpose.LOGIN_2FA: "login verification",
}


class OtpService:
    def __init__(self, db: Session):
        self.repo = OtpRepository(db)

    def _enforce_resend_cooldown(self, destination: str, purpose: OtpPurpose) -> None:
        """Prevents spamming OTP requests faster than OTP_RESEND_COOLDOWN_SECONDS."""
        most_recent = self.repo.get_most_recent(destination, purpose)
        if most_recent is None:
            return
        elapsed = (datetime.utcnow() - most_recent.created_at).total_seconds()
        if elapsed < settings.OTP_RESEND_COOLDOWN_SECONDS:
            wait = int(settings.OTP_RESEND_COOLDOWN_SECONDS - elapsed)
            raise TooManyRequestsException(f"Please wait {wait} seconds before requesting another OTP.")

    async def send_email_otp(
        self, email: str, purpose: OtpPurpose, user_id: Optional[int] = None
    ) -> None:
        self._enforce_resend_cooldown(email, purpose)

        code = generate_secure_code(settings.OTP_LENGTH)
        expires_at = datetime.utcnow() + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)

        self.repo.create({
            "user_id": user_id,
            "destination": email,
            "channel": OtpChannel.EMAIL,
            "purpose": purpose,
            "hashed_otp": hash_token(code),
            "attempts": 0,
            "is_used": False,
            "expires_at": expires_at,
        })

        await EmailService.send_otp_email(email, code, _PURPOSE_LABELS[purpose], settings.OTP_EXPIRE_MINUTES)

    async def send_mobile_otp(
        self, mobile_number: str, purpose: OtpPurpose, user_id: Optional[int] = None
    ) -> None:
        self._enforce_resend_cooldown(mobile_number, purpose)

        code = generate_secure_code(settings.OTP_LENGTH)
        expires_at = datetime.utcnow() + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)

        self.repo.create({
            "user_id": user_id,
            "destination": mobile_number,
            "channel": OtpChannel.SMS,
            "purpose": purpose,
            "hashed_otp": hash_token(code),
            "attempts": 0,
            "is_used": False,
            "expires_at": expires_at,
        })

        await SmsService.send_otp_sms(mobile_number, code, settings.OTP_EXPIRE_MINUTES)

    def verify_otp(self, destination: str, purpose: OtpPurpose, otp_code: str) -> bool:
        """
        Verifies a submitted OTP code. Raises OtpException on failure (expired,
        not found, wrong code, or max attempts exceeded). On success, marks the
        OTP record as used so it cannot be replayed.
        """
        record = self.repo.get_latest_active(destination, purpose)
        if record is None:
            raise OtpException("OTP has expired or does not exist. Please request a new one.")

        if record.attempts >= settings.OTP_MAX_ATTEMPTS:
            raise OtpException("Maximum verification attempts exceeded. Please request a new OTP.")

        record.attempts += 1

        if not constant_time_compare(hash_token(otp_code.strip()), record.hashed_otp):
            self.repo.db.add(record)
            self.repo.db.commit()
            remaining = settings.OTP_MAX_ATTEMPTS - record.attempts
            raise OtpException(f"Incorrect OTP code. {remaining} attempt(s) remaining.")

        record.is_used = True
        self.repo.db.add(record)
        self.repo.db.commit()
        return True
