"""
BuildCore Custom Exceptions.

All exceptions inherit from BuildCoreError and carry a structured
error code, message, and optional details dict for the API response.
"""

from typing import Any


class BuildCoreError(Exception):
    """Base exception for all BuildCore application errors.

    Attributes:
        code: Machine-readable error code (e.g. "NOT_FOUND").
        message: Human-readable error description.
        details: Optional dict with extra context (field-level info, etc.).
        status_code: HTTP status code (default 500).
    """

    def __init__(
        self,
        code: str = "INTERNAL_ERROR",
        message: str = "An unexpected error occurred",
        details: dict[str, Any] | None = None,
        status_code: int = 500,
    ) -> None:
        self.code = code
        self.message = message
        self.details = details or {}
        self.status_code = status_code
        super().__init__(self.message)


class NotFoundError(BuildCoreError):
    """Raised when a requested resource does not exist (HTTP 404)."""

    def __init__(
        self,
        message: str = "Resource not found",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            code="NOT_FOUND",
            message=message,
            details=details,
            status_code=404,
        )


class ConflictError(BuildCoreError):
    """Raised on duplicate / state-conflict violations (HTTP 409)."""

    def __init__(
        self,
        message: str = "Resource conflict",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            code="CONFLICT",
            message=message,
            details=details,
            status_code=409,
        )


class UnauthorizedError(BuildCoreError):
    """Raised when authentication is missing or invalid (HTTP 401)."""

    def __init__(
        self,
        message: str = "Authentication required",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            code="UNAUTHORIZED",
            message=message,
            details=details,
            status_code=401,
        )


class ForbiddenError(BuildCoreError):
    """Raised when the caller lacks permission (HTTP 403)."""

    def __init__(
        self,
        message: str = "Access denied",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            code="FORBIDDEN",
            message=message,
            details=details,
            status_code=403,
        )


class ValidationError(BuildCoreError):
    """Raised on request validation failures (HTTP 422)."""

    def __init__(
        self,
        message: str = "Validation error",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            code="VALIDATION_ERROR",
            message=message,
            details=details,
            status_code=422,
        )


class TenantError(BuildCoreError):
    """Raised on multi-tenant isolation / resolution failures."""

    def __init__(
        self,
        message: str = "Tenant error",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            code="TENANT_ERROR",
            message=message,
            details=details,
            status_code=400,
        )
