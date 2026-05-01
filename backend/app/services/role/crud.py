"""Role CRUD operations — low-level database access.

All queries filter out soft-deleted records (deleted_at IS NULL).
System roles (organization_id IS NULL) are included in queries.
"""

import json
from datetime import datetime, timezone

from sqlalchemy import func, select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.role import Role
from app.models.user_permission_override import UserPermissionOverride


async def get_role_by_id(db: AsyncSession, role_id: str) -> Role | None:
    """Fetch a single role by ID (excludes soft-deleted).

    Args:
        db: Async database session.
        role_id: UUID string of the role.

    Returns:
        Role row or None if not found / deleted.
    """
    stmt = select(Role).where(
        Role.id == role_id,
        Role.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def list_roles(
    db: AsyncSession,
    org_id: str,
    page: int = 1,
    per_page: int = 20,
) -> tuple[list[Role], int]:
    """List roles available to an organization (org-scoped + system roles).

    Returns org-specific roles for the given org_id plus all system roles
    (where organization_id IS NULL).

    Args:
        db: Async database session.
        org_id: UUID string of the organization.
        page: 1-based page index.
        per_page: Items per page.

    Returns:
        Tuple of (items, total_count).
    """
    base_filter = or_(
        Role.organization_id == org_id,
        Role.organization_id.is_(None),
    ) & (Role.deleted_at.is_(None))

    # Count
    count_stmt = select(func.count()).select_from(Role).where(base_filter)
    total = (await db.execute(count_stmt)).scalar_one()

    # Fetch page
    offset = (page - 1) * per_page
    stmt = (
        select(Role)
        .where(base_filter)
        .order_by(Role.is_system_role.desc(), Role.created_at.asc())
        .offset(offset)
        .limit(per_page)
    )
    result = await db.execute(stmt)
    items = list(result.scalars().all())

    return items, total


async def create_role(db: AsyncSession, **kwargs: object) -> Role:
    """Create a new role and flush to the session.

    If permissions is a list, it will be serialized to JSON string.

    Args:
        db: Async database session.
        **kwargs: Column values for the new Role.

    Returns:
        The new Role instance (id populated after flush).
    """
    if "permissions" in kwargs and isinstance(kwargs["permissions"], list):
        kwargs["permissions"] = json.dumps(kwargs["permissions"])

    role = Role(**kwargs)
    db.add(role)
    await db.flush()
    return role


async def update_role(
    db: AsyncSession,
    role_id: str,
    **kwargs: object,
) -> Role | None:
    """Update a role by ID.

    Refuses to update system roles (is_system_role = True).

    Args:
        db: Async database session.
        role_id: UUID string of the role.
        **kwargs: Column values to update.

    Returns:
        Updated Role row or None if not found.

    Raises:
        BuildCoreError: If the role is a system role.
    """
    from app.core.exceptions import BuildCoreError

    stmt = select(Role).where(
        Role.id == role_id,
        Role.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    role = result.scalar_one_or_none()
    if role is None:
        return None

    if role.is_system_role:
        raise BuildCoreError(
            code="FORBIDDEN",
            message="Cannot modify a system role",
            status_code=403,
        )

    if "permissions" in kwargs and isinstance(kwargs["permissions"], list):
        kwargs["permissions"] = json.dumps(kwargs["permissions"])

    for key, value in kwargs.items():
        if value is not None:
            setattr(role, key, value)

    await db.flush()
    return role


async def delete_role(db: AsyncSession, role_id: str) -> bool:
    """Soft-delete a role.

    Refuses to delete system roles (is_system_role = True).

    Args:
        db: Async database session.
        role_id: UUID string of the role.

    Returns:
        True if the role was found and soft-deleted, False if not found.

    Raises:
        BuildCoreError: If the role is a system role.
    """
    from app.core.exceptions import BuildCoreError

    stmt = select(Role).where(
        Role.id == role_id,
        Role.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    role = result.scalar_one_or_none()
    if role is None:
        return False

    if role.is_system_role:
        raise BuildCoreError(
            code="FORBIDDEN",
            message="Cannot delete a system role",
            status_code=403,
        )

    role.deleted_at = datetime.now(timezone.utc)
    await db.flush()
    return True


async def get_permission_overrides(
    db: AsyncSession,
    user_id: str,
) -> list[UserPermissionOverride]:
    """Fetch all active permission overrides for a user.

    Only non-expired overrides are returned.

    Args:
        db: Async database session.
        user_id: UUID string of the user.

    Returns:
        List of UserPermissionOverride rows.
    """
    now = datetime.now(timezone.utc)
    stmt = select(UserPermissionOverride).where(
        UserPermissionOverride.user_id == user_id,
        or_(
            UserPermissionOverride.expires_at.is_(None),
            UserPermissionOverride.expires_at > now,
        ),
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())
