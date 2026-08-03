"""
app/middlewares/security_headers.py
---------------------------------------
Adds standard security response headers to every response:
- X-Content-Type-Options: nosniff           -> stops browsers MIME-sniffing responses (XSS vector)
- X-Frame-Options: DENY                     -> prevents clickjacking via iframes
- Content-Security-Policy                   -> restricts script/style sources (defense-in-depth XSS mitigation)
- Strict-Transport-Security                 -> forces HTTPS on supporting browsers (prod only)
- Referrer-Policy                           -> avoids leaking full URLs to third parties
- X-XSS-Protection                          -> legacy header, harmless to include for older browsers
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.core.config import settings


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; img-src 'self' data:; script-src 'self'; style-src 'self' 'unsafe-inline'"
        )

        if settings.APP_ENV != "development":
            response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"

        return response
