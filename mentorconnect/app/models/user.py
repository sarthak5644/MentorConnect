"""
app/models/user.py
-------------------
Core identity models: Role and User.
Every account (super admin, mentor, student) is a row in `users`, linked to a
`roles` row for RBAC. Student/Mentor specific data lives in their own tables
(one-to-one extension pattern) to keep `users` lean and role-agnostic.
"""

from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, ForeignKey, Enum as SAEnum
)
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base_class import Base, TimestampMixin
from app.models.enums import RoleName, UserStatus


class Role(Base, TimestampMixin):
    """
    Lookup table for RBAC roles: super_admin, mentor, student.
    Kept as a table (not just an enum on users) so permissions/metadata
    can be extended later without a schema migration on `users`.
    """
    id = Column(Integer, primary_key=True, index=True)
    name = Column(SAEnum(RoleName), unique=True, nullable=False, index=True)
    description = Column(String(255), nullable=True)

    users = relationship("User", back_populates="role")


class User(Base, TimestampMixin):
    """
    Central account table for ALL platform users regardless of role.
    Role-specific profile data is stored in `students` / `mentors` tables,
    each linked 1:1 via user_id foreign key.
    """
    id = Column(Integer, primary_key=True, index=True)

    full_name = Column(String(150), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    mobile_number = Column(String(20), unique=True, nullable=True, index=True)

    # Passwords are NEVER stored in plain text - always bcrypt hashed (see core/security.py)
    hashed_password = Column(String(255), nullable=False)

    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False, index=True)

    status = Column(SAEnum(UserStatus), default=UserStatus.PENDING, nullable=False, index=True)

    is_email_verified = Column(Boolean, default=False, nullable=False)
    is_mobile_verified = Column(Boolean, default=False, nullable=False)

    profile_image_url = Column(String(500), nullable=True)

    # Used to invalidate all existing refresh tokens at once (e.g. on password change, logout-all)
    token_version = Column(Integer, default=0, nullable=False)

    last_login_at = Column(DateTime, nullable=True)
    blocked_at = Column(DateTime, nullable=True)
    blocked_reason = Column(String(255), nullable=True)

    # ---------------- Relationships ----------------
    role = relationship("Role", back_populates="users")
    student_profile = relationship("Student", back_populates="user", uselist=False, cascade="all, delete-orphan")
    mentor_profile = relationship(
    "Mentor",
    back_populates="user",
    uselist=False,
    cascade="all, delete-orphan",
    foreign_keys="Mentor.user_id",
)

    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    otp_verifications = relationship("OtpVerification", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="actor", foreign_keys="AuditLog.actor_user_id")

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email}>"
