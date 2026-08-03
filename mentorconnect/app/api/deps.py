"""
app/api/deps.py
------------------
Reusable FastAPI dependencies: DB session, current user extraction from JWT,
and role-based access control (RBAC) guards.

Usage in a router:
    @router.get("/me")
    def me(current_user: User = Depends(get_current_user)):
        ...

    @router.post("/admin-only")
    def admin_action(current_user: User = Depends(require_roles(RoleName.SUPER_ADMIN))):
        ...
"""

from typing import Callable, Optional
from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import decode_access_token
from app.core.exceptions import UnauthorizedException, ForbiddenException
from app.models.user import User
from app.models.enums import RoleName, UserStatus
from app.repositories.user_repository import UserRepository

# tokenUrl is just used by Swagger UI to know where to POST for a token; the actual
# login endpoint lives at /api/v1/auth/login (see api/v1/endpoints/auth.py)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login", auto_error=False)


def get_current_user(
    request: Request,
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Decodes the JWT access token from the Authorization header, loads the
    corresponding User, and verifies the account is still active and the
    token hasn't been invalidated (token_version mismatch = logged out/password changed).
    """
    if not token:
        raise UnauthorizedException("Not authenticated. Please provide a valid access token.")

    try:
        payload = decode_access_token(token)
    except JWTError:
        raise UnauthorizedException("Invalid or expired access token.")

    user_id_raw = payload.get("sub")
    token_version = payload.get("tv")
    if user_id_raw is None or token_version is None:
        raise UnauthorizedException("Malformed access token.")

    user_repo = UserRepository(db)
    user = user_repo.get_with_role(int(user_id_raw))

    if user is None:
        raise UnauthorizedException("User account no longer exists.")

    if user.token_version != token_version:
        raise UnauthorizedException("Session has expired. Please log in again.")

    if user.status == UserStatus.BLOCKED:
        raise ForbiddenException("Your account has been blocked. Contact support for assistance.")

    if user.status == UserStatus.DEACTIVATED:
        raise ForbiddenException("Your account has been deactivated.")

    # Stash request context for audit logging downstream (see services/audit_service.py)
    request.state.current_user_id = user.id
    return user


def require_roles(*allowed_roles: RoleName) -> Callable[..., User]:
    """
    Dependency factory enforcing RBAC: only users whose role is in `allowed_roles`
    may proceed. Raises 403 otherwise.
    """

    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role.name not in allowed_roles:
            raise ForbiddenException(
                f"This action requires one of the following roles: {[r.value for r in allowed_roles]}"
            )
        return current_user

    return role_checker


def get_current_active_verified_user(current_user: User = Depends(get_current_user)) -> User:
    """Stricter guard for actions that require a fully verified account (email + mobile)."""
    if not current_user.is_email_verified:
        raise ForbiddenException("Please verify your email address before performing this action.")
    return current_user
