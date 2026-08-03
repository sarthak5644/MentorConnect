"""
app/middlewares/csrf.py
---------------------------
Double-submit-cookie CSRF protection for state-changing requests.

Why this approach: MentorConnect's primary auth is a Bearer JWT sent via the
Authorization header (which browsers do NOT attach automatically to
cross-site requests the way they do cookies), so classic CSRF risk is already
low for token-based API calls. However, to defend any cookie-based session
use (e.g. if a frontend stores the refresh token in an httponly cookie) and
to satisfy the explicit "CSRF Protection" requirement, we implement the
double-submit-cookie pattern:
  1. The server issues a `csrf_token` cookie (readable by JS, NOT httponly).
  2. The frontend must echo that value back in the `X-CSRF-Token` header on
     any unsafe method (POST/PUT/PATCH/DELETE).
  3. We reject the request if the header is missing or doesn't match the cookie.

Safe methods (GET/HEAD/OPTIONS) and a configurable exempt-path list (e.g. the
login/register endpoints, which run before any CSRF cookie could exist) skip
this check.
"""

import hmac
import secrets
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse

from app.core.config import settings

CSRF_COOKIE_NAME = "csrf_token"
CSRF_HEADER_NAME = "x-csrf-token"
SAFE_METHODS = {"GET", "HEAD", "OPTIONS", "TRACE"}

# Paths that issue/consume tokens before a CSRF cookie could realistically exist,
# and paths that are protected purely by Bearer-token auth (not cookies) and thus
# carry no CSRF risk in the double-submit-cookie sense.
EXEMPT_PATH_PREFIXES = (
    f"{settings.API_V1_PREFIX}/auth/",
    f"{settings.API_V1_PREFIX}/docs",
    f"{settings.API_V1_PREFIX}/openapi.json",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/health",
)


class CSRFMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Always ensure a CSRF cookie exists for the client to read & echo back later.
        existing_cookie = request.cookies.get(CSRF_COOKIE_NAME)

        if request.method in SAFE_METHODS or any(
            request.url.path.startswith(p) for p in EXEMPT_PATH_PREFIXES
        ):
            response: Response = await call_next(request)
        else:
            header_token = request.headers.get(CSRF_HEADER_NAME)
            if not existing_cookie or not header_token or not hmac.compare_digest(existing_cookie, header_token):
                return JSONResponse(
                    status_code=403,
                    content={
                        "success": False,
                        "error_code": "CSRF_VALIDATION_FAILED",
                        "message": "CSRF token missing or invalid. Include the X-CSRF-Token header "
                                   "matching your csrf_token cookie on state-changing requests.",
                    },
                )
            response = await call_next(request)

        if not existing_cookie:
            new_token = secrets.token_hex(32)
            response.set_cookie(
                key=CSRF_COOKIE_NAME,
                value=new_token,
                httponly=False,  # must be JS-readable so the frontend can echo it in the header
                secure=settings.APP_ENV != "development",
                samesite="strict",
                max_age=60 * 60 * 24,
            )

        return response
