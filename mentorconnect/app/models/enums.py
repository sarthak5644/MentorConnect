"""
app/models/enums.py
--------------------
Centralized Python Enums used as column types across the schema.
Using Enum (rather than free-text strings) enforces valid values at the DB level
and gives clear autocomplete/type-safety in code.
"""

import enum


class RoleName(str, enum.Enum):
    SUPER_ADMIN = "super_admin"
    MENTOR = "mentor"
    STUDENT = "student"


class UserStatus(str, enum.Enum):
    ACTIVE = "active"
    BLOCKED = "blocked"
    PENDING = "pending"        # awaiting email/mobile verification
    DEACTIVATED = "deactivated"


class MentorApprovalStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class DocumentStatus(str, enum.Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"


class SlotStatus(str, enum.Enum):
    AVAILABLE = "available"
    BOOKED = "booked"
    BLOCKED = "blocked"        # mentor manually blocked the slot


class MentorshipRequestStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class BookingStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class NotificationType(str, enum.Enum):
    MENTORSHIP_REQUEST = "mentorship_request"
    BOOKING = "booking"
    CHAT_MESSAGE = "chat_message"
    SYSTEM = "system"
    ACCOUNT = "account"
    COMPLAINT = "complaint"


class ComplaintStatus(str, enum.Enum):
    OPEN = "open"
    IN_REVIEW = "in_review"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"


class OtpPurpose(str, enum.Enum):
    EMAIL_VERIFICATION = "email_verification"
    MOBILE_VERIFICATION = "mobile_verification"
    PASSWORD_RESET = "password_reset"
    LOGIN_2FA = "login_2fa"


class OtpChannel(str, enum.Enum):
    EMAIL = "email"
    SMS = "sms"


class MessageType(str, enum.Enum):
    TEXT = "text"
    IMAGE = "image"
    FILE = "file"


class AuditAction(str, enum.Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    APPROVE = "approve"
    REJECT = "reject"
    BLOCK = "block"
    UNBLOCK = "unblock"
    OTHER = "other"
