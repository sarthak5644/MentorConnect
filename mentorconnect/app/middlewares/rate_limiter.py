"""
app/middlewares/rate_limiter.py
-----------------------------------
Rate limiting configuration using slowapi (a Flask-limiter-style wrapper for
Starlette/FastAPI). Limits are keyed by client IP address. Sensitive endpoints
(login, OTP requests) get tighter limits than the general default to mitigate
brute-force and SMS/email-bombing abuse.

Usage on a specific route:
    @router.post("/login")
    @limiter.limit(settings.RATE_LIMIT_LOGIN)
    def login(request: Request, ...):
        ...

Note: slowapi requires the route function's first parameter to be named
`request` and typed as `Request` for the limiter to access client info.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[settings.RATE_LIMIT_DEFAULT],
    headers_enabled=True,  # adds X-RateLimit-* response headers for client visibility
)
