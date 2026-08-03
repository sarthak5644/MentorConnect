"""
app/core/exceptions.py
-------------------------
Custom exception hierarchy for domain/business errors. Routers and services
raise these instead of raw HTTPException, keeping business logic decoupled
from FastAPI/HTTP specifics. The global exception handler (see
app/middlewares/exception_handler.py) converts these into consistent JSON
error responses with the right HTTP status code.
"""


class AppException(Exception):
    """Base class for all application-level exceptions."""

    status_code: int = 500
    error_code: str = "INTERNAL_ERROR"

    def __init__(self, detail: str = "An unexpected error occurred.", error_code: str | None = None):
        self.detail = detail
        if error_code:
            self.error_code = error_code
        super().__init__(detail)


class NotFoundException(AppException):
    status_code = 404
    error_code = "NOT_FOUND"

    def __init__(self, detail: str = "Resource not found."):
        super().__init__(detail, "NOT_FOUND")


class BadRequestException(AppException):
    status_code = 400
    error_code = "BAD_REQUEST"

    def __init__(self, detail: str = "Invalid request."):
        super().__init__(detail, "BAD_REQUEST")


class UnauthorizedException(AppException):
    status_code = 401
    error_code = "UNAUTHORIZED"

    def __init__(self, detail: str = "Authentication required or invalid credentials."):
        super().__init__(detail, "UNAUTHORIZED")


class ForbiddenException(AppException):
    status_code = 403
    error_code = "FORBIDDEN"

    def __init__(self, detail: str = "You do not have permission to perform this action."):
        super().__init__(detail, "FORBIDDEN")


class ConflictException(AppException):
    status_code = 409
    error_code = "CONFLICT"

    def __init__(self, detail: str = "Resource conflict."):
        super().__init__(detail, "CONFLICT")


class UnprocessableEntityException(AppException):
    status_code = 422
    error_code = "UNPROCESSABLE_ENTITY"

    def __init__(self, detail: str = "Unprocessable entity."):
        super().__init__(detail, "UNPROCESSABLE_ENTITY")


class TooManyRequestsException(AppException):
    status_code = 429
    error_code = "TOO_MANY_REQUESTS"

    def __init__(self, detail: str = "Too many requests. Please try again later."):
        super().__init__(detail, "TOO_MANY_REQUESTS")


class FileUploadException(AppException):
    status_code = 400
    error_code = "FILE_UPLOAD_ERROR"

    def __init__(self, detail: str = "File upload failed."):
        super().__init__(detail, "FILE_UPLOAD_ERROR")


class OtpException(AppException):
    status_code = 400
    error_code = "OTP_ERROR"

    def __init__(self, detail: str = "OTP verification failed."):
        super().__init__(detail, "OTP_ERROR")


class CaptchaException(AppException):
    status_code = 400
    error_code = "CAPTCHA_ERROR"

    def __init__(self, detail: str = "Captcha verification failed."):
        super().__init__(detail, "CAPTCHA_ERROR")
