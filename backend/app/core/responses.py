"""
BuildCore Standard API Response Helpers.

Every endpoint returns a consistent JSON envelope with
success flag, data, message, and optional meta.
"""

from typing import Any

from app.core.exceptions import BuildCoreError


def success_response(
    data: Any = None,
    message: str = "Success",
    meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a standard success envelope.

    Args:
        data: Primary response payload (list, dict, or None).
        message: Short human-readable status message.
        meta: Optional metadata (pagination info, counts, etc.).

    Returns:
        Dict with success=True, data, message, and meta keys.
    """
    return {
        "success": True,
        "data": data,
        "message": message,
        "meta": meta,
    }


def error_response(error: BuildCoreError) -> dict[str, Any]:
    """Build a standard error envelope from a BuildCoreError.

    Args:
        error: Any subclass of BuildCoreError.

    Returns:
        Dict with success=False and nested error object containing
        code, message, and details.
    """
    return {
        "success": False,
        "error": {
            "code": error.code,
            "message": error.message,
            "details": error.details,
        },
    }


def paginated_response(
    data: list[Any],
    page: int,
    per_page: int,
    total: int,
    message: str = "Success",
) -> dict[str, Any]:
    """Build a paginated success response.

    Args:
        data: List of items for the current page.
        page: Current page number (1-based).
        per_page: Number of items per page.
        total: Total number of items across all pages.
        message: Optional status message.

    Returns:
        Success response with pagination metadata in the meta field.
    """
    total_pages = compute_total_pages(total, per_page)
    meta = {
        "page": page,
        "per_page": per_page,
        "total": total,
        "total_pages": total_pages,
    }
    return success_response(data=data, message=message, meta=meta)


def compute_total_pages(total: int, per_page: int) -> int:
    """Ceiling division: total items / per_page.

    Args:
        total: Total number of items.
        per_page: Items per page.

    Returns:
        Number of pages (minimum 0).
    """
    if per_page <= 0 or total <= 0:
        return 0
    return (total + per_page - 1) // per_page
