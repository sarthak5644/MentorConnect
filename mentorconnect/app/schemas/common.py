"""
app/schemas/common.py
------------------------
Shared base schemas: generic API response envelope, pagination params/response,
and a common ORM-mode base config so every schema doesn't repeat boilerplate.
"""

from typing import Generic, TypeVar, Optional, List, Any
from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class ORMBase(BaseModel):
    """Base schema for any model returned directly from SQLAlchemy ORM objects."""
    model_config = ConfigDict(from_attributes=True)


class ApiResponse(BaseModel, Generic[T]):
    """Standard success response envelope used by most endpoints."""
    success: bool = True
    message: str = "Success"
    data: Optional[T] = None


class PaginationParams(BaseModel):
    """Common query params for paginated list endpoints."""
    page: int = Field(default=1, ge=1, description="Page number, starting at 1")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page (max 100)")

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


class PaginatedResponse(BaseModel, Generic[T]):
    """Standard paginated list response envelope."""
    success: bool = True
    message: str = "Success"
    total: int
    page: int
    page_size: int
    total_pages: int
    data: List[T]


class ErrorResponse(BaseModel):
    """Standard error response shape returned by the global exception handler."""
    success: bool = False
    error_code: str
    message: str
    details: Optional[Any] = None
