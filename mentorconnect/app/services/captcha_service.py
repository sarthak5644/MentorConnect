"""
app/services/captcha_service.py
-----------------------------------
Generates distorted-text image captchas (PNG, base64-encoded) using Pillow,
and validates user-submitted answers against the hashed answer stored in
captcha_sessions. Implemented directly with Pillow (rather than depending on
a third-party captcha-generation library) to keep the dependency surface
small and avoid relying on a package whose exact API can't be verified here.
"""

import base64
import io
import random
import secrets
import uuid
from datetime import datetime, timedelta
from typing import Tuple

from PIL import Image, ImageDraw, ImageFilter, ImageFont
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import hash_token, constant_time_compare
from app.core.exceptions import CaptchaException
from app.repositories.captcha_repository import CaptchaRepository

# Characters chosen to avoid visually ambiguous pairs (0/O, 1/I/l) for better UX
_CAPTCHA_ALPHABET = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"


def _random_captcha_text(length: int) -> str:
    return "".join(secrets.choice(_CAPTCHA_ALPHABET) for _ in range(length))


def _render_captcha_image(text: str, width: int, height: int) -> bytes:
    """Draws the captcha text onto a noisy, distorted background and returns PNG bytes."""
    image = Image.new("RGB", (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)

    # Background noise lines (visual clutter to hinder automated OCR)
    for _ in range(8):
        start = (random.randint(0, width), random.randint(0, height))
        end = (random.randint(0, width), random.randint(0, height))
        draw.line([start, end], fill=tuple(random.randint(150, 220) for _ in range(3)), width=1)

    # Try to use a built-in truetype font if available; fall back to PIL's default bitmap font.
    font = None
    for font_candidate_size in (40, 36, 32):
        try:
            font = ImageFont.truetype("DejaVuSans-Bold.ttf", font_candidate_size)
            break
        except (OSError, IOError):
            continue
    if font is None:
        font = ImageFont.load_default()

    # Draw each character individually with random rotation/position for distortion
    char_spacing = width // (len(text) + 1)
    for i, char in enumerate(text):
        char_img = Image.new("RGBA", (60, 60), (255, 255, 255, 0))
        char_draw = ImageDraw.Draw(char_img)
        color = tuple(random.randint(20, 100) for _ in range(3))
        char_draw.text((10, 5), char, font=font, fill=color)
        rotated = char_img.rotate(random.randint(-25, 25), expand=True, fillcolor=(255, 255, 255, 0))

        x = char_spacing * (i + 1) - 20 + random.randint(-5, 5)
        y = random.randint(5, max(5, height - 50))
        image.paste(rotated, (x, y), rotated)

    # Foreground noise dots
    for _ in range(60):
        xy = (random.randint(0, width), random.randint(0, height))
        draw.point(xy, fill=tuple(random.randint(100, 180) for _ in range(3)))

    image = image.filter(ImageFilter.SMOOTH)

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


class CaptchaService:
    def __init__(self, db: Session):
        self.repo = CaptchaRepository(db)

    def generate_captcha(self) -> Tuple[str, str, int]:
        """
        Creates a new captcha challenge, persists its hashed answer, and returns
        (session_id, base64_png_image, expires_in_seconds) for the API response.
        """
        text = _random_captcha_text(settings.CAPTCHA_LENGTH)
        image_bytes = _render_captcha_image(text, settings.CAPTCHA_WIDTH, settings.CAPTCHA_HEIGHT)
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")

        session_id = uuid.uuid4().hex
        expires_at = datetime.utcnow() + timedelta(minutes=settings.CAPTCHA_EXPIRE_MINUTES)

        # Answers are case-insensitive for usability; we normalize before hashing.
        self.repo.create({
            "session_id": session_id,
            "hashed_answer": hash_token(text.upper()),
            "is_used": False,
            "expires_at": expires_at,
        })

        return session_id, image_base64, settings.CAPTCHA_EXPIRE_MINUTES * 60

    def validate_captcha(self, session_id: str, answer: str, mark_used: bool = True) -> bool:
        """
        Validates a captcha answer. Raises CaptchaException on any failure
        (missing/expired session, already used, or wrong answer) so callers
        get a consistent error without needing to check a boolean themselves.
        """
        session = self.repo.get_active_by_session_id(session_id)
        if session is None:
            raise CaptchaException("Captcha session is invalid, expired, or already used. Please try again.")

        submitted_hash = hash_token(answer.strip().upper())
        if not constant_time_compare(submitted_hash, session.hashed_answer):
            raise CaptchaException("Incorrect captcha answer.")

        if mark_used:
            session.is_used = True
            self.repo.db.add(session)
            self.repo.db.commit()

        return True
