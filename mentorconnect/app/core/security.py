"""
app/core/security.py
----------------------
Password hashing (bcrypt) and JWT token creation/verification.
This is the single source of truth for all cryptographic auth operations -
no other module should hash passwords or encode/decode JWTs directly.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Optional
import hashlib
import hmac
import secrets

from jose import jwt, JWTError
from passlib.context import CryptContext

from app.core.config import settings

# ---------------------------------------------------------------------------
# Password hashing (bcrypt via passlib)
# ---------------------------------------------------------------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=settings.BCRYPT_ROUNDS)


def hash_password(plain_password: str) -> str:
    """Hash a plain-text password using bcrypt. Never store plain passwords."""
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain-text password against its bcrypt hash."""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except (ValueError, TypeError):
        return False


# ---------------------------------------------------------------------------
# JWT Access & Refresh Tokens
# ---------------------------------------------------------------------------
TOKEN_TYPE_ACCESS = "access"
TOKEN_TYPE_REFRESH = "refresh"


def create_access_token(
    subject: str,
    role: str,
    token_version: int,
    extra_claims: Optional[dict] = None,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Create a short-lived JWT access token.
    `subject` is the user id (as string), `role` is embedded for fast RBAC checks
    without a DB hit on every request. `token_version` lets us invalidate tokens
    issued before a password change / forced logout.
    """
    now = datetime.now(timezone.utc)
    expire = now + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))

    payload = {
        "sub": subject,
        "role": role,
        "tv": token_version,
        "type": TOKEN_TYPE_ACCESS,
        "iat": now,
        "exp": expire,
        "jti": secrets.token_hex(16),  # unique token id, useful for tracing/blacklisting
    }
    if extra_claims:
        payload.update(extra_claims)

    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(
    subject: str,
    token_version: int,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Create a long-lived JWT refresh token, signed with a SEPARATE secret key
    from the access token. This way, leaking the access-token secret doesn't
    automatically compromise refresh tokens (defense in depth).
    """
    now = datetime.now(timezone.utc)
    expire = now + (expires_delta or timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS))

    payload = {
        "sub": subject,
        "tv": token_version,
        "type": TOKEN_TYPE_REFRESH,
        "iat": now,
        "exp": expire,
        "jti": secrets.token_hex(16),
    }
    return jwt.encode(payload, settings.JWT_REFRESH_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any]:
    """Decode & verify an access token. Raises JWTError if invalid/expired."""
    payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    if payload.get("type") != TOKEN_TYPE_ACCESS:
        raise JWTError("Invalid token type: expected access token")
    return payload


def decode_refresh_token(token: str) -> dict[str, Any]:
    """Decode & verify a refresh token. Raises JWTError if invalid/expired."""
    payload = jwt.decode(token, settings.JWT_REFRESH_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    if payload.get("type") != TOKEN_TYPE_REFRESH:
        raise JWTError("Invalid token type: expected refresh token")
    return payload


def hash_token(raw_token: str) -> str:
    """
    Deterministic SHA-256 hash of a refresh token for DB storage/lookup.
    We use SHA-256 (not bcrypt) here because we need fast, deterministic lookups
    by hash (bcrypt is intentionally slow & non-deterministic per call).
    """
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def generate_secure_code(length: int = 6) -> str:
    """Generate a cryptographically secure numeric code (used for OTPs)."""
    return "".join(secrets.choice("0123456789") for _ in range(length))


def constant_time_compare(a: str, b: str) -> bool:
    """Timing-safe string comparison to prevent timing attacks on secret comparisons."""
    return hmac.compare_digest(a.encode("utf-8"), b.encode("utf-8"))
