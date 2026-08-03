"""
app/models/__init__.py
------------------------
Imports every model so that `Base.metadata` is fully populated when Alembic
(or `Base.metadata.create_all`) inspects it. Without these imports, Alembic's
autogenerate would miss tables that are never imported elsewhere.
"""

from app.db.base_class import Base  # noqa: F401

from app.models.user import Role, User  # noqa: F401
from app.models.category import Category, Field, mentor_fields  # noqa: F401
from app.models.student import Student  # noqa: F401
from app.models.mentor import Mentor  # noqa: F401
from app.models.mentor_document import MentorDocument  # noqa: F401
from app.models.availability_slot import MentorAvailabilitySlot  # noqa: F401
from app.models.mentorship_request import MentorshipRequest  # noqa: F401
from app.models.booking import Booking  # noqa: F401
from app.models.chat import Chat, Message  # noqa: F401
from app.models.notification import Notification  # noqa: F401
from app.models.rating import Rating  # noqa: F401
from app.models.complaint import Complaint  # noqa: F401
from app.models.otp_verification import OtpVerification  # noqa: F401
from app.models.captcha_session import CaptchaSession  # noqa: F401
from app.models.audit_log import AuditLog  # noqa: F401
from app.models.refresh_token import RefreshToken  # noqa: F401

__all__ = [
    "Base", "Role", "User", "Category", "Field", "mentor_fields",
    "Student", "Mentor", "MentorDocument", "MentorAvailabilitySlot",
    "MentorshipRequest", "Booking", "Chat", "Message", "Notification",
    "Rating", "Complaint", "OtpVerification", "CaptchaSession", "AuditLog",
    "RefreshToken",
]
