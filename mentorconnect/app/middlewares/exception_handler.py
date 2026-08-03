"""
app/middlewares/exception_handler.py
----------------------------------------
Global exception handlers registered on the FastAPI app. Converts every
exception type (our custom AppException hierarchy, Pydantic validation
errors, SQLAlchemy errors, and any uncaught Exception) into a consistent
JSON error envelope, and ensures unexpected errors are logged with full
context without ever leaking internals (stack traces, SQL, secrets) to the client.
"""

import traceback
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.exceptions import AppException
from app.core.logger import logger
from app.core.config import settings


def _error_response(status_code: int, error_code: str, message: str, details=None) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "error_code": error_code,
            "message": message,
            "details": details,
        },
    )


def register_exception_handlers(app: FastAPI) -> None:

    @app.exception_handler(AppException)
    async def handle_app_exception(request: Request, exc: AppException):
        logger.warning(f"AppException [{exc.error_code}] at {request.url.path}: {exc.detail}")
        return _error_response(exc.status_code, exc.error_code, exc.detail)

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(request: Request, exc: RequestValidationError):
        # Pydantic validation errors - return field-level details to help the client fix their request
        logger.info(f"Validation error at {request.url.path}: {exc.errors()}")
        simplified = [
            {"field": ".".join(str(loc) for loc in err["loc"]), "message": err["msg"]}
            for err in exc.errors()
        ]
        return _error_response(
            status.HTTP_422_UNPROCESSABLE_ENTITY, "VALIDATION_ERROR",
            "Request validation failed.", details=simplified,
        )

    @app.exception_handler(StarletteHTTPException)
    async def handle_http_exception(request: Request, exc: StarletteHTTPException):
        logger.warning(f"HTTPException {exc.status_code} at {request.url.path}: {exc.detail}")
        return _error_response(exc.status_code, "HTTP_ERROR", str(exc.detail))

    @app.exception_handler(IntegrityError)
    async def handle_integrity_error(request: Request, exc: IntegrityError):
        # Typically a unique constraint violation (duplicate email, double-booking, etc.)
        logger.warning(f"IntegrityError at {request.url.path}: {exc}")
        return _error_response(
            status.HTTP_409_CONFLICT, "DATA_CONFLICT",
            "This operation conflicts with existing data (e.g. a duplicate or already-used resource).",
        )

    @app.exception_handler(SQLAlchemyError)
    async def handle_sqlalchemy_error(request: Request, exc: SQLAlchemyError):
        logger.error(f"Database error at {request.url.path}: {exc}\n{traceback.format_exc()}")
        return _error_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR, "DATABASE_ERROR",
            "A database error occurred. Please try again later.",
        )

    @app.exception_handler(Exception)
    async def handle_unhandled_exception(request: Request, exc: Exception):
        # Last-resort catch-all: log full traceback server-side, but never expose it to the client.
        logger.error(f"Unhandled exception at {request.url.path}: {exc}\n{traceback.format_exc()}")
        details = str(exc) if settings.APP_DEBUG else None
        return _error_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR, "INTERNAL_ERROR",
            "An unexpected error occurred. Please try again later.", details=details,
        )
