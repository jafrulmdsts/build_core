"""
BuildCore Pagination Utilities.

Provides parameter parsing, offset calculation, and total-pages
helpers for list endpoints.
"""

from dataclasses import dataclass

from fastapi import Query


@dataclass(frozen=True)
class PaginationParams:
    """Immutable container for validated pagination parameters.

    Attributes:
        page: 1-based page index (minimum 1).
        per_page: Number of items per page (clamped to max_per_page).
        max_per_page: Upper cap for per_page (for security / perf).
    """

    page: int = 1
    per_page: int = 20
    max_per_page: int = 100


def get_pagination_params(
    page: int = Query(default=1, ge=1, description="Page number (1-based)"),
    per_page: int = Query(default=20, ge=1, le=100, description="Items per page"),
) -> PaginationParams:
    """FastAPI dependency that parses and validates pagination query params.

    Args:
        page: Requested page number (must be >= 1).
        per_page: Requested page size (must be >= 1).

    Returns:
        PaginationParams with clamped per_page.
    """
    clamped_per_page = min(per_page, PaginationParams.max_per_page)
    return PaginationParams(page=page, per_page=clamped_per_page)


def compute_offset(params: PaginationParams) -> int:
    """Convert page number to a SQL OFFSET value.

    Args:
        params: Validated PaginationParams.

    Returns:
        Zero-based offset for the query.
    """
    return (params.page - 1) * params.per_page


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
