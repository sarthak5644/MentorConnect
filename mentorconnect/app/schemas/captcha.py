"""
app/schemas/captcha.py
-------------------------
Schemas for the image captcha challenge/response flow.
"""

from pydantic import BaseModel


class CaptchaResponse(BaseModel):
    """Returned when a new captcha is generated."""
    session_id: str
    image_base64: str   # PNG image encoded as base64 data URI, ready for <img src="data:image/png;base64,...">
    expires_in_seconds: int


class CaptchaValidateRequest(BaseModel):
    session_id: str
    answer: str
