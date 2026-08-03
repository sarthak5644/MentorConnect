"""
app/middlewares/request_logger.py
-------------------------------------
Logs every incoming request (method, path, status code, duration, client IP)
for observability. This is separate from the audit_log table - this is
operational/infrastructure logging, audit_log is business-event logging.
"""

import time
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.core.logger import logger


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = uuid.uuid4().hex[:12]
        request.state.request_id = request_id
        start_time = time.perf_counter()

        client_ip = request.client.host if request.client else "unknown"
        logger.info(f"[{request_id}] --> {request.method} {request.url.path} from {client_ip}")

        try:
            response = await call_next(request)
        except Exception:
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.error(f"[{request_id}] <-- {request.method} {request.url.path} FAILED after {duration_ms:.1f}ms")
            raise

        duration_ms = (time.perf_counter() - start_time) * 1000
        response.headers["X-Request-ID"] = request_id
        logger.info(
            f"[{request_id}] <-- {request.method} {request.url.path} "
            f"status={response.status_code} duration={duration_ms:.1f}ms"
        )
        return response
