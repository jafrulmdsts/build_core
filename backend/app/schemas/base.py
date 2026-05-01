"""
Base Pydantic schemas for standard API response envelope.

All responses use camelCase field names for the API layer.
"""

from typing import Any, Generic, TypeVar
from pydantic import BaseModel, Field


T = TypeVar("T")


class PaginationMeta(BaseModel):
    """Pagination metadata returned with list endpoints."""

    page: int = Field(..., description="Current page number (1-based)")
    per_page: int = Field(..., description="Items per page")
    total: int = Field(..., description="Total items across all pages")
    total_pages: int = Field(..., description="Total number of pages")


class ErrorDetail(BaseModel):
    """Single error detail entry."""

    code: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable error message")
    details: dict[str, Any] = Field(default_factory=dict)


class SuccessResponse(BaseModel, Generic[T]):
    """Standard success response envelope."""

    success: bool = True
    data: T | None = None
    message: str = "Success"
    meta: PaginationMeta | dict[str, Any] | None = None


class ErrorResponse(BaseModel):
    """Standard error response envelope."""

    success: bool = False
    error: ErrorDetail


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated success response with metadata."""

    success: bool = True
    data: list[T]
    message: str = "Success"
    meta: PaginationMeta
