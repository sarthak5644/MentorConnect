"""
app/services/email_service.py
---------------------------------
Handles sending transactional emails (OTP codes, password reset, welcome
emails, mentor approval/rejection notices) via SMTP using aiosmtplib.
In APP_ENV=development without SMTP credentials configured, falls back to
logging the email content instead of actually sending (so local dev never
needs real SMTP creds to exercise OTP flows end-to-end).
"""

from email.message import EmailMessage
from typing import Optional
import aiosmtplib

from app.core.config import settings
from app.core.logger import logger


class EmailService:
    @staticmethod
    async def send_email(to_email: str, subject: str, html_body: str, text_body: Optional[str] = None) -> bool:
        """
        Send an HTML email. Returns True on success, False on failure (failures are
        logged but never raised - a notification failure should not break the user's
        primary action, e.g. registration should still succeed even if the welcome
        email fails to send).
        """
        if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
            # No SMTP configured (typical for local dev) - log instead of sending for real.
            logger.info(f"[DEV EMAIL] To: {to_email} | Subject: {subject}\n{text_body or html_body}")
            return True

        message = EmailMessage()
        message["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
        message["To"] = to_email
        message["Subject"] = subject
        message.set_content(text_body or "Please view this email in an HTML-compatible client.")
        message.add_alternative(html_body, subtype="html")

        try:
            await aiosmtplib.send(
                message,
                hostname=settings.SMTP_HOST,
                port=settings.SMTP_PORT,
                username=settings.SMTP_USER,
                password=settings.SMTP_PASSWORD,
                start_tls=settings.SMTP_USE_TLS,
            )
            logger.info(f"Email sent successfully to {to_email}: {subject}")
            return True
        except Exception as exc:
            logger.error(f"Failed to send email to {to_email}: {exc}")
            return False

    @staticmethod
    async def send_otp_email(to_email: str, otp_code: str, purpose_label: str, expire_minutes: int) -> bool:
        subject = f"Your MentorConnect verification code: {otp_code}"
        html_body = f"""
        <div style="font-family: Arial, sans-serif; max-width: 480px; margin: auto;">
            <h2 style="color:#2563eb;">MentorConnect</h2>
            <p>Your one-time password (OTP) for <strong>{purpose_label}</strong> is:</p>
            <p style="font-size: 28px; font-weight: bold; letter-spacing: 4px;">{otp_code}</p>
            <p>This code will expire in {expire_minutes} minutes. If you did not request this, please ignore this email.</p>
        </div>
        """
        text_body = f"Your MentorConnect OTP for {purpose_label} is {otp_code}. It expires in {expire_minutes} minutes."
        return await EmailService.send_email(to_email, subject, html_body, text_body)

    @staticmethod
    async def send_mentor_approval_email(
        to_email: str, full_name: str, approved: bool, reason: Optional[str] = None
    ) -> bool:
        if approved:
            subject = "Your MentorConnect mentor application has been approved!"
            html_body = f"""
            <div style="font-family: Arial, sans-serif; max-width: 480px; margin: auto;">
                <h2 style="color:#16a34a;">Congratulations, {full_name}!</h2>
                <p>Your mentor profile has been reviewed and <strong>approved</strong>.
                You can now appear in student search results and start accepting mentorship requests.</p>
            </div>
            """
        else:
            subject = "Update on your MentorConnect mentor application"
            html_body = f"""
            <div style="font-family: Arial, sans-serif; max-width: 480px; margin: auto;">
                <h2 style="color:#dc2626;">Hello {full_name},</h2>
                <p>We were unable to approve your mentor application at this time.</p>
                <p><strong>Reason:</strong> {reason or "Did not meet verification requirements."}</p>
                <p>You're welcome to update your profile and documents and reapply.</p>
            </div>
            """
        return await EmailService.send_email(to_email, subject, html_body)
