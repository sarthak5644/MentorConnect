"""
app/services/sms_service.py
-------------------------------
Handles sending SMS messages (mobile OTPs) via a pluggable provider.
Default provider is "console" (logs the SMS instead of sending - safe for
local dev with zero external dependencies). Swap SMS_PROVIDER=twilio in .env
and fill in Twilio credentials to send real SMS in production.
"""

from app.core.config import settings
from app.core.logger import logger


class SmsService:
    @staticmethod
    async def send_sms(mobile_number: str, message: str) -> bool:
        """
        Dispatches an SMS through the configured provider.
        Returns True on success, False on failure (never raises - SMS failure
        should not break the calling flow; the OTP record still exists and the
        user can request a resend).
        """
        provider = settings.SMS_PROVIDER.lower()

        if provider == "console":
            logger.info(f"[DEV SMS] To: {mobile_number} | Message: {message}")
            return True

        if provider == "twilio":
            return await SmsService._send_via_twilio(mobile_number, message)

        logger.error(f"Unknown SMS provider configured: {provider}")
        return False

    @staticmethod
    async def _send_via_twilio(mobile_number: str, message: str) -> bool:
        """
        Sends SMS via Twilio's REST API using httpx (no twilio SDK dependency needed).
        Requires TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_NUMBER in .env.
        """
        import httpx

        if not (settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN and settings.TWILIO_FROM_NUMBER):
            logger.error("Twilio SMS provider selected but credentials are not fully configured.")
            return False

        url = f"https://api.twilio.com/2010-04-01/Accounts/{settings.TWILIO_ACCOUNT_SID}/Messages.json"
        data = {
            "From": settings.TWILIO_FROM_NUMBER,
            "To": mobile_number,
            "Body": message,
        }
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    url, data=data,
                    auth=(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN),
                )
            if response.status_code in (200, 201):
                logger.info(f"SMS sent successfully to {mobile_number} via Twilio")
                return True
            logger.error(f"Twilio SMS failed ({response.status_code}): {response.text}")
            return False
        except Exception as exc:
            logger.error(f"Failed to send SMS via Twilio to {mobile_number}: {exc}")
            return False

    @staticmethod
    async def send_otp_sms(mobile_number: str, otp_code: str, expire_minutes: int) -> bool:
        message = (
            f"Your MentorConnect verification code is {otp_code}. "
            f"It expires in {expire_minutes} minutes. Do not share this code."
        )
        return await SmsService.send_sms(mobile_number, message)
