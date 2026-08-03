"""
app/services/auth_service.py
--------------------------------
Core authentication business logic: student/mentor registration, login,
token refresh/rotation, logout, and password management. This is the
heart of the auth system - routers stay thin and just call into here.
"""

from datetime import datetime, timedelta
from typing import Optional, Tuple

from fastapi import Request
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import (
    hash_password, verify_password, create_access_token, create_refresh_token,
    decode_refresh_token, hash_token,
)
from app.core.exceptions import (
    BadRequestException, UnauthorizedException, ConflictException, ForbiddenException,
)
from app.models.enums import RoleName, UserStatus, AuditAction
from app.models.user import User
from app.repositories.user_repository import UserRepository, RoleRepository
from app.repositories.student_repository import StudentRepository
from app.repositories.mentor_repository import MentorRepository
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.repositories.category_repository import FieldRepository
from app.services.captcha_service import CaptchaService
from app.services.audit_service import AuditService
from app.schemas.user import StudentRegisterRequest, MentorRegisterRequest, TokenPair


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.role_repo = RoleRepository(db)
        self.student_repo = StudentRepository(db)
        self.mentor_repo = MentorRepository(db)
        self.refresh_token_repo = RefreshTokenRepository(db)
        self.field_repo = FieldRepository(db)
        self.captcha_service = CaptchaService(db)
        self.audit_service = AuditService(db)

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------
    def _validate_unique_contact(self, email: str, mobile_number: str) -> None:
        if self.user_repo.email_exists(email):
            raise ConflictException("An account with this email already exists.")
        if self.user_repo.mobile_exists(mobile_number):
            raise ConflictException("An account with this mobile number already exists.")

    def register_student(self, payload: StudentRegisterRequest, request: Optional[Request] = None) -> User:
        self.captcha_service.validate_captcha(payload.captcha_session_id, payload.captcha_answer)
        self._validate_unique_contact(payload.email, payload.mobile_number)

        role = self.role_repo.get_by_name(RoleName.STUDENT)
        if role is None:
            raise BadRequestException("Student role is not configured on this system.")

        user = self.user_repo.create({
            "full_name": payload.full_name,
            "email": payload.email,
            "mobile_number": payload.mobile_number,
            "hashed_password": hash_password(payload.password),
            "role_id": role.id,
            "status": UserStatus.PENDING,
        })

        self.student_repo.create({
            "user_id": user.id,
            "institution_name": payload.institution_name,
            "education_level": payload.education_level,
            "field_of_study": payload.field_of_study,
        })

        self.audit_service.log(
            AuditAction.CREATE, actor_user_id=user.id, entity_type="User",
            entity_id=user.id, description="Student registered", request=request,
        )
        return user

    def register_mentor(self, payload: MentorRegisterRequest, request: Optional[Request] = None) -> User:
        self.captcha_service.validate_captcha(payload.captcha_session_id, payload.captcha_answer)
        self._validate_unique_contact(payload.email, payload.mobile_number)

        role = self.role_repo.get_by_name(RoleName.MENTOR)
        if role is None:
            raise BadRequestException("Mentor role is not configured on this system.")

        user = self.user_repo.create({
            "full_name": payload.full_name,
            "email": payload.email,
            "mobile_number": payload.mobile_number,
            "hashed_password": hash_password(payload.password),
            "role_id": role.id,
            "status": UserStatus.PENDING,
        })

        mentor = self.mentor_repo.create({
            "user_id": user.id,
            "headline": payload.headline,
            "years_of_experience": payload.years_of_experience,
            "current_organization": payload.current_organization,
            "designation": payload.designation,
            "hourly_rate": payload.hourly_rate,
        })

        if payload.expertise_field_ids:
            fields = self.field_repo.get_many_by_ids(payload.expertise_field_ids)
            mentor.expertise_fields = fields
            self.db.add(mentor)
            self.db.commit()

        self.audit_service.log(
            AuditAction.CREATE, actor_user_id=user.id, entity_type="User",
            entity_id=user.id, description="Mentor registered (pending approval)", request=request,
        )
        return user

    # ------------------------------------------------------------------
    # Login / Token issuance
    # ------------------------------------------------------------------
    def authenticate(self, email: str, password: str, captcha_session_id: str, captcha_answer: str) -> User:
        self.captcha_service.validate_captcha(captcha_session_id, captcha_answer)

        user = self.user_repo.get_by_email(email)
        if user is None or not verify_password(password, user.hashed_password):
            raise UnauthorizedException("Incorrect email or password.")

        if user.status == UserStatus.BLOCKED:
            raise ForbiddenException(
                f"Your account has been blocked. Reason: {user.blocked_reason or 'Policy violation.'}"
            )

        if user.status == UserStatus.DEACTIVATED:
            raise ForbiddenException("Your account has been deactivated.")

        return user

    def issue_tokens(self, user: User, request: Optional[Request] = None) -> TokenPair:
        """Issues a fresh access + refresh token pair, persisting the refresh token hash for revocation."""
        access_token = create_access_token(str(user.id), user.role.name.value, user.token_version)
        refresh_token = create_refresh_token(str(user.id), user.token_version)

        expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        self.refresh_token_repo.create({
            "user_id": user.id,
            "token_hash": hash_token(refresh_token),
            "is_revoked": False,
            "expires_at": expires_at,
            "user_agent": request.headers.get("user-agent") if request else None,
            "ip_address": request.client.host if request and request.client else None,
        })

        user.last_login_at = datetime.utcnow()
        self.db.add(user)
        self.db.commit()

        return TokenPair(access_token=access_token, refresh_token=refresh_token)

    def login(
        self, email: str, password: str, captcha_session_id: str, captcha_answer: str,
        request: Optional[Request] = None,
    ) -> Tuple[User, TokenPair]:
        user = self.authenticate(email, password, captcha_session_id, captcha_answer)
        tokens = self.issue_tokens(user, request)
        self.audit_service.log(
            AuditAction.LOGIN, actor_user_id=user.id, entity_type="User",
            entity_id=user.id, description="User logged in", request=request,
        )
        return user, tokens

    # ------------------------------------------------------------------
    # Refresh / Logout
    # ------------------------------------------------------------------
    def refresh_access_token(self, refresh_token: str) -> TokenPair:
        """
        Validates a refresh token (signature + DB record not revoked/expired),
        then ROTATES it: the old refresh token is revoked and a brand new
        access+refresh pair is issued. Rotation limits the blast radius if a
        refresh token is ever leaked.
        """
        try:
            payload = decode_refresh_token(refresh_token)
        except JWTError:
            raise UnauthorizedException("Invalid or expired refresh token.")

        token_hash = hash_token(refresh_token)
        db_record = self.refresh_token_repo.get_active_by_hash(token_hash)
        if db_record is None:
            raise UnauthorizedException("Refresh token has been revoked or expired. Please log in again.")

        user = self.user_repo.get_with_role(int(payload["sub"]))
        if user is None or user.token_version != payload.get("tv"):
            raise UnauthorizedException("Session is no longer valid. Please log in again.")

        if user.status in (UserStatus.BLOCKED, UserStatus.DEACTIVATED):
            raise ForbiddenException("This account is no longer active.")

        # Rotate: revoke the used refresh token, issue a brand new pair
        self.refresh_token_repo.revoke(token_hash)

        new_access = create_access_token(str(user.id), user.role.name.value, user.token_version)
        new_refresh = create_refresh_token(str(user.id), user.token_version)
        expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        self.refresh_token_repo.create({
            "user_id": user.id,
            "token_hash": hash_token(new_refresh),
            "is_revoked": False,
            "expires_at": expires_at,
        })

        return TokenPair(access_token=new_access, refresh_token=new_refresh)

    def logout(self, refresh_token: str) -> None:
        """Revokes a single refresh token (logout this device/session)."""
        self.refresh_token_repo.revoke(hash_token(refresh_token))

    def logout_all_sessions(self, user: User) -> None:
        """
        Revokes ALL refresh tokens for a user AND bumps token_version, which
        instantly invalidates every access token already issued too
        (even ones not yet expired) - used for 'logout everywhere' or after
        a password change / suspected compromise.
        """
        self.refresh_token_repo.revoke_all_for_user(user.id)
        user.token_version += 1
        self.db.add(user)
        self.db.commit()

    # ------------------------------------------------------------------
    # Password management
    # ------------------------------------------------------------------
    def change_password(self, user: User, current_password: str, new_password: str) -> None:
        if not verify_password(current_password, user.hashed_password):
            raise UnauthorizedException("Current password is incorrect.")
        user.hashed_password = hash_password(new_password)
        user.token_version += 1  # invalidate all existing sessions on password change
        self.db.add(user)
        self.db.commit()
        self.refresh_token_repo.revoke_all_for_user(user.id)

    def reset_password(self, email: str, new_password: str) -> None:
        """Called after OTP verification has already succeeded for PASSWORD_RESET purpose."""
        user = self.user_repo.get_by_email(email)
        if user is None:
            raise BadRequestException("No account found with this email.")
        user.hashed_password = hash_password(new_password)
        user.token_version += 1
        self.db.add(user)
        self.db.commit()
        self.refresh_token_repo.revoke_all_for_user(user.id)
