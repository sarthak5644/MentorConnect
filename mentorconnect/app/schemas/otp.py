"""
app/schemas/otp.py
---------------------
Schemas for requesting and verifying Email/Mobile OTPs.
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
from app.models.enums import OtpPurpose
from app.schemas.user import MOBILE_REGEX


class EmailOtpRequest(BaseModel):
    email: EmailStr
    purpose: OtpPurpose = OtpPurpose.EMAIL_VERIFICATION


class MobileOtpRequest(BaseModel):
    mobile_number: str = Field(..., min_length=8, max_length=20)
    purpose: OtpPurpose = OtpPurpose.MOBILE_VERIFICATION

    @field_validator("mobile_number")
    @classmethod
    def validate_mobile(cls, v: str) -> str:
        if not MOBILE_REGEX.match(v):
            raise ValueError("Invalid mobile number format. Use international format e.g. +911234567890")
        return v


class OtpVerifyRequest(BaseModel):
    destination: str = Field(..., description="Email address or mobile number the OTP was sent to")
    otp_code: str = Field(..., min_length=4, max_length=10)
    purpose: OtpPurpose
