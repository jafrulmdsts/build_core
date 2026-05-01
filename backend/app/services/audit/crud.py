"""Audit log CRUD operations — low-level database access.

AuditLog is immutable and has no soft-delete (no deleted_at column).
All records are preserved indefinitely.
"""

import json
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog


async def create_audit_log(
    db: AsyncSession,
    organization_id: str | None = None,
    user_id: str | None = None,
    action: str = "",
    table_name: str | None = None,
    record_id: str | None = None,
    old_values: dict[str, Any] | None = None,
    new_values: dict[str, Any] | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> AuditLog:
    """Insert a new audit log entry and flush.

    old_values and new_values dicts are serialized to JSON strings.

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

    Returns:
        The new AuditLog instance.
    """
    log = AuditLog(
        organization_id=organization_id,
        user_id=user_id,
        action=action,
        table_name=table_name,
        record_id=record_id,
        old_values=json.dumps(old_values) if old_values is not None else None,
        new_values=json.dumps(new_values) if new_values is not None else None,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    db.add(log)
    await db.flush()
    return log


async def list_audit_logs(
    db: AsyncSession,
    organization_id: str,
    page: int = 1,
    per_page: int = 20,
) -> tuple[list[AuditLog], int]:
    """List audit logs for an organization with pagination.

    Args:
        db: Async database session.
        organization_id: UUID string of the organization.
        page: 1-based page index.
        per_page: Items per page.

    Returns:
        Tuple of (items, total_count).
    """
    base_filter = AuditLog.organization_id == organization_id

    # Count
    count_stmt = select(func.count()).select_from(AuditLog).where(base_filter)
    total = (await db.execute(count_stmt)).scalar_one()

    # Fetch page
    offset = (page - 1) * per_page
    stmt = (
        select(AuditLog)
        .where(base_filter)
        .order_by(AuditLog.created_at.desc())
        .offset(offset)
        .limit(per_page)
    )
    result = await db.execute(stmt)
    items = list(result.scalars().all())

    return items, total
