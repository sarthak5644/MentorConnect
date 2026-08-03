"""
app/api/v1/endpoints/otp.py
-------------------------------
Endpoints for requesting and verifying email/mobile OTPs (used for account
verification after registration, and can be reused for other OTP-gated flows).
"""

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_user
from app.middlewares.rate_limiter import limiter
from app.core.config import settings
from app.models.user import User
from app.models.enums import OtpPurpose, UserStatus
from app.services.otp_service import OtpService
from app.repositories.user_repository import UserRepository
from app.schemas.common import ApiResponse
from app.schemas.otp import EmailOtpRequest, MobileOtpRequest, OtpVerifyRequest

router = APIRouter(prefix="/otp", tags=["OTP Verification"])


@router.post("/email/send", response_model=ApiResponse[None], summary="Send an OTP to an email address")
@limiter.limit(settings.RATE_LIMIT_OTP)
async def send_email_otp(
    request: Request, payload: EmailOtpRequest, db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = OtpService(db)
    await service.send_email_otp(payload.email, payload.purpose, user_id=current_user.id)
    return ApiResponse(message=f"OTP sent to {payload.email}.")


@router.post("/mobile/send", response_model=ApiResponse[None], summary="Send an OTP to a mobile number")
@limiter.limit(settings.RATE_LIMIT_OTP)
async def send_mobile_otp(
    request: Request, payload: MobileOtpRequest, db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = OtpService(db)
    await service.send_mobile_otp(payload.mobile_number, payload.purpose, user_id=current_user.id)
    return ApiResponse(message=f"OTP sent to {payload.mobile_number}.")


@router.post("/verify", response_model=ApiResponse[None], summary="Verify an OTP code")
def verify_otp(
    payload: OtpVerifyRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user),
):
    service = OtpService(db)
    service.verify_otp(payload.destination, payload.purpose, payload.otp_code)

    # If this was an account verification OTP, flip the corresponding flag on the User,
    # and activate the account once both email and mobile are verified.
    if payload.purpose == OtpPurpose.EMAIL_VERIFICATION and payload.destination == current_user.email:
        current_user.is_email_verified = True
        if current_user.status == UserStatus.PENDING and current_user.is_mobile_verified:
            current_user.status = UserStatus.ACTIVE
        db.add(current_user)
        db.commit()
    elif payload.purpose == OtpPurpose.MOBILE_VERIFICATION and payload.destination == current_user.mobile_number:
        current_user.is_mobile_verified = True
        if current_user.status == UserStatus.PENDING and current_user.is_email_verified:
            current_user.status = UserStatus.ACTIVE
        db.add(current_user)
        db.commit()

    return ApiResponse(message="OTP verified successfully.")
