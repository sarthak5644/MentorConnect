"""
app/api/v1/endpoints/auth.py
--------------------------------
Authentication endpoints: registration (student/mentor), login, token
refresh, logout, password change/reset, and image captcha issuance.
"""

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_user
from app.middlewares.rate_limiter import limiter
from app.core.config import settings
from app.core.exceptions import OtpException
from app.models.user import User
from app.models.enums import OtpPurpose
from app.services.auth_service import AuthService
from app.services.captcha_service import CaptchaService
from app.services.otp_service import OtpService
from app.schemas.common import ApiResponse
from app.schemas.user import (
    StudentRegisterRequest, MentorRegisterRequest, LoginRequest, LoginResponse,
    RefreshTokenRequest, TokenPair, UserOut, ChangePasswordRequest,
    ForgotPasswordRequest, ResetPasswordRequest,
)
from app.schemas.captcha import CaptchaResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.get("/captcha", response_model=ApiResponse[CaptchaResponse], summary="Generate a new image captcha")
def get_captcha(db: Session = Depends(get_db)):
    """
    Returns a base64-encoded PNG captcha image and a session_id.
    The client must submit both the session_id and the user's typed answer
    back on registration/login/forgot-password to prove they are not a bot.
    """
    service = CaptchaService(db)
    session_id, image_base64, expires_in = service.generate_captcha()
    return ApiResponse(
        message="Captcha generated successfully.",
        data=CaptchaResponse(session_id=session_id, image_base64=image_base64, expires_in_seconds=expires_in),
    )


@router.post(
    "/register/student", response_model=ApiResponse[UserOut],
    status_code=status.HTTP_201_CREATED, summary="Register a new student account",
)
@limiter.limit(settings.RATE_LIMIT_LOGIN)
def register_student(request: Request, payload: StudentRegisterRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    user = service.register_student(payload, request)
    return ApiResponse(message="Student registered successfully. Please verify your email and mobile.", data=user)


@router.post(
    "/register/mentor", response_model=ApiResponse[UserOut],
    status_code=status.HTTP_201_CREATED, summary="Register a new mentor account (pending admin approval)",
)
@limiter.limit(settings.RATE_LIMIT_LOGIN)
def register_mentor(request: Request, payload: MentorRegisterRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    user = service.register_mentor(payload, request)
    return ApiResponse(
        message="Mentor registered successfully. Your profile is pending admin approval.", data=user,
    )


@router.post("/login", response_model=ApiResponse[LoginResponse], summary="Login with email and password")
@limiter.limit(settings.RATE_LIMIT_LOGIN)
def login(request: Request, payload: LoginRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    user, tokens = service.login(
        payload.email, payload.password, payload.captcha_session_id, payload.captcha_answer, request,
    )
    return ApiResponse(
        message="Login successful.",
        data=LoginResponse(user=UserOut.model_validate(user), tokens=tokens),
    )


@router.post(
    "/refresh", response_model=ApiResponse[TokenPair],
    summary="Exchange a refresh token for a new token pair",
)
def refresh_token(payload: RefreshTokenRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    tokens = service.refresh_access_token(payload.refresh_token)
    return ApiResponse(message="Token refreshed successfully.", data=tokens)


@router.post("/logout", response_model=ApiResponse[None], summary="Logout from the current session/device")
def logout(payload: RefreshTokenRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    service.logout(payload.refresh_token)
    return ApiResponse(message="Logged out successfully.")


@router.post("/logout-all", response_model=ApiResponse[None], summary="Logout from all devices/sessions")
def logout_all(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    service = AuthService(db)
    service.logout_all_sessions(current_user)
    return ApiResponse(message="Logged out from all sessions successfully.")


@router.post("/change-password", response_model=ApiResponse[None], summary="Change password while logged in")
def change_password(
    payload: ChangePasswordRequest, db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = AuthService(db)
    service.change_password(current_user, payload.current_password, payload.password)
    return ApiResponse(message="Password changed successfully. Please log in again.")


@router.post("/forgot-password", response_model=ApiResponse[None], summary="Request a password-reset OTP via email")
@limiter.limit(settings.RATE_LIMIT_OTP)
async def forgot_password(request: Request, payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    captcha_service = CaptchaService(db)
    captcha_service.validate_captcha(payload.captcha_session_id, payload.captcha_answer)

    otp_service = OtpService(db)
    # Always respond with the same generic message whether or not the email exists,
    # to avoid leaking which emails are registered (user enumeration protection).
    from app.repositories.user_repository import UserRepository
    user = UserRepository(db).get_by_email(payload.email)
    if user is not None:
        await otp_service.send_email_otp(payload.email, OtpPurpose.PASSWORD_RESET, user_id=user.id)

    return ApiResponse(message="If an account with this email exists, a password reset OTP has been sent.")


@router.post("/reset-password", response_model=ApiResponse[None], summary="Reset password using OTP")
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    otp_service = OtpService(db)
    otp_service.verify_otp(payload.email, OtpPurpose.PASSWORD_RESET, payload.otp_code)

    auth_service = AuthService(db)
    auth_service.reset_password(payload.email, payload.password)
    return ApiResponse(message="Password reset successfully. Please log in with your new password.")


@router.get("/me", response_model=ApiResponse[UserOut], summary="Get the currently authenticated user's profile")
def get_me(current_user: User = Depends(get_current_user)):
    return ApiResponse(data=UserOut.model_validate(current_user))
