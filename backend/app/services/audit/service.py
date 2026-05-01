"""Audit log service layer — business logic and convenience helpers.

Provides a high-level interface for recording and querying audit events.
"""

from datetime import datetime
from typing import Any

from app.services.audit import crud


async def get_audit_logs(
    db,
    organization_id: str,
    page: int = 1,
    per_page: int = 20,
) -> dict:
    """Get paginated audit logs for an organization.

    Args:
        db: Async database session.
        organization_id: UUID string of the organization.
        page: 1-based page index.
        per_page: Items per page.

    Returns:
        Dict with items, pagination metadata.
    """
    items, total = await crud.list_audit_logs(db, organization_id, page, per_page)
    total_pages = (total + per_page - 1) // per_page if per_page > 0 else 0

    log_items = []
    for log in items:
        log_items.append({
            "id": log.id,
            "created_at": log.created_at,
            "organization_id": log.organization_id,
            "user_id": log.user_id,
            "action": log.action,
            "table_name": log.table_name,
            "record_id": log.record_id,
            "old_values": log.old_values,
            "new_values": log.new_values,
            "ip_address": log.ip_address,
            "user_agent": log.user_agent,
        })

    return {
        "items": log_items,
        "page": page,
        "per_page": per_page,
        "total": total,
        "total_pages": total_pages,
    }


async def log_action(
    db,
    *,
    organization_id: str | None = None,
    user_id: str | None = None,
    action: str,
    table_name: str | None = None,
    record_id: str | None = None,
    old_values: dict[str, Any] | None = None,
    new_values: dict[str, Any] | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> None:
    """Convenience function to create an audit log entry.

    This is the primary entry point for recording audit events
    from other services.

    Args:
        db: Async database session.
        organization_id: Optional organization context.
        user_id: Optional user context.
        action: Action identifier (e.g. "user.create").
        table_name: Database table affected.
        record_id: Primary key of affected record.
        old_values: Previous state dict.
        new_values: New state dict.
        ip_address: Client IP address.
        user_agent: Client user-agent string.
    """
    await crud.create_audit_log(
        db,
        organization_id=organization_id,
        user_id=user_id,
        action=action,
        table_name=table_name,
        record_id=record_id,
        old_values=old_values,
        new_values=new_values,
        ip_address=ip_address,
        user_agent=user_agent,
    )
