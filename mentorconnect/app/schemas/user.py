"""
app/schemas/user.py
----------------------
Pydantic schemas for User entity: registration input, login input, public
output representation, and password-related operations. Validation here is
the first line of defense against malformed/malicious input (XSS, SQLi payloads
in strings are inert against SQLAlchemy parameterized queries, but we still
constrain shapes and lengths defensively).
"""

import re
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict

from app.models.enums import RoleName, UserStatus


PASSWORD_REGEX = re.compile(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&#^()_\-+=]).{8,64}$"
)
MOBILE_REGEX = re.compile(r"^\+?[1-9]\d{7,14}$")  # E.164-ish: optional +, 8-15 digits


class PasswordMixin(BaseModel):
    password: str = Field(..., min_length=8, max_length=64)

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if not PASSWORD_REGEX.match(v):
            raise ValueError(
                "Password must be 8-64 characters and include at least one uppercase letter, "
                "one lowercase letter, one digit, and one special character."
            )
        return v


class UserRegisterBase(PasswordMixin):
    """Shared fields for both student and mentor registration."""
    full_name: str = Field(..., min_length=2, max_length=150)
    email: EmailStr
    mobile_number: str = Field(..., min_length=8, max_length=20)

    # Anti-bot protections required on every public registration call
    captcha_session_id: str = Field(..., description="Session ID from /auth/captcha")
    captcha_answer: str = Field(..., min_length=1, max_length=20)

    @field_validator("mobile_number")
    @classmethod
    def validate_mobile(cls, v: str) -> str:
        if not MOBILE_REGEX.match(v):
            raise ValueError("Invalid mobile number format. Use international format e.g. +911234567890")
        return v

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, v: str) -> str:
        # Strip whitespace and reject names containing HTML/script tags (basic XSS guard;
        # full sanitization is also applied centrally in utils/sanitizer.py)
        v = v.strip()
        if re.search(r"[<>]", v):
            raise ValueError("Full name contains invalid characters.")
        return v


class StudentRegisterRequest(UserRegisterBase):
    institution_name: Optional[str] = Field(None, max_length=200)
    education_level: Optional[str] = Field(None, max_length=100)
    field_of_study: Optional[str] = Field(None, max_length=150)


class MentorRegisterRequest(UserRegisterBase):
    headline: Optional[str] = Field(None, max_length=200)
    years_of_experience: int = Field(default=0, ge=0, le=80)
    current_organization: Optional[str] = Field(None, max_length=200)
    designation: Optional[str] = Field(None, max_length=150)
    hourly_rate: float = Field(default=0.0, ge=0)
    expertise_field_ids: list[int] = Field(default_factory=list)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1, max_length=64)
    captcha_session_id: str
    captcha_answer: str = Field(..., min_length=1, max_length=20)


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class RoleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: RoleName


class UserOut(BaseModel):
    """Public-safe representation of a User - never includes hashed_password."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    email: EmailStr
    mobile_number: Optional[str] = None
    status: UserStatus
    is_email_verified: bool
    is_mobile_verified: bool
    profile_image_url: Optional[str] = None
    role: RoleOut
    created_at: datetime


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class LoginResponse(BaseModel):
    user: UserOut
    tokens: TokenPair


class ChangePasswordRequest(PasswordMixin):
    current_password: str = Field(..., min_length=1, max_length=64)


class ForgotPasswordRequest(BaseModel):
    email: EmailStr
    captcha_session_id: str
    captcha_answer: str = Field(..., min_length=1, max_length=20)


class ResetPasswordRequest(PasswordMixin):
    email: EmailStr
    otp_code: str = Field(..., min_length=4, max_length=10)


class UpdateProfileRequest(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=150)

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if re.search(r"[<>]", v):
            raise ValueError("Full name contains invalid characters.")
        return v
