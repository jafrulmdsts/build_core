"""Organization CRUD operations — low-level database access.

All queries filter out soft-deleted records (deleted_at IS NULL).
"""

from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization import Organization


async def get_org_by_id(db: AsyncSession, org_id: str) -> Organization | None:
    """Fetch a single organization by ID (excludes soft-deleted).

    Args:
        db: Async database session.
        org_id: UUID string of the organization.

    Returns:
        Organization row or None if not found / deleted.
    """
    stmt = select(Organization).where(
        Organization.id == org_id,
        Organization.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_org_by_slug(db: AsyncSession, slug: str) -> Organization | None:
    """Fetch a single organization by slug (excludes soft-deleted).

    Args:
        db: Async database session.
        slug: URL-friendly slug string.

    Returns:
        Organization row or None if not found / deleted.
    """
    stmt = select(Organization).where(
        Organization.slug == slug,
        Organization.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def list_orgs(
    db: AsyncSession,
    page: int = 1,
    per_page: int = 20,
) -> tuple[list[Organization], int]:
    """List organizations with pagination (excludes soft-deleted).

    Args:
        db: Async database session.
        page: 1-based page index.
        per_page: Items per page.

    Returns:
        Tuple of (items, total_count).
    """
    base_filter = Organization.deleted_at.is_(None)

    # Count
    count_stmt = select(func.count()).select_from(Organization).where(base_filter)
    total = (await db.execute(count_stmt)).scalar_one()

    # Fetch page
    offset = (page - 1) * per_page
    stmt = (
        select(Organization)
        .where(base_filter)
        .order_by(Organization.created_at.desc())
        .offset(offset)
        .limit(per_page)
    )
    result = await db.execute(stmt)
    items = list(result.scalars().all())

    return items, total


async def create_org(db: AsyncSession, **kwargs: object) -> Organization:
    """Create a new organization and flush to the session.

    Args:
        db: Async database session.
        **kwargs: Column values for the new Organization.

    Returns:
        The new Organization instance (id populated after flush).
    """
    org = Organization(**kwargs)
    db.add(org)
    await db.flush()
    return org


async def update_org(
    db: AsyncSession,
    org_id: str,
    **kwargs: object,
) -> Organization | None:
    """Update an organization by ID (excludes soft-deleted).

    Args:
        db: Async database session.
        org_id: UUID string of the organization.
        **kwargs: Column values to update.

    Returns:
        Updated Organization row or None if not found.
    """
    stmt = select(Organization).where(
        Organization.id == org_id,
        Organization.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    org = result.scalar_one_or_none()
    if org is None:
        return None

    for key, value in kwargs.items():
        if value is not None:
            setattr(org, key, value)

    await db.flush()
    return org


async def delete_org(db: AsyncSession, org_id: str) -> bool:
    """Soft-delete an organization by setting deleted_at.

    Args:
        db: Async database session.
        org_id: UUID string of the organization.

    Returns:
        True if the org was found and soft-deleted, False otherwise.
    """
    stmt = select(Organization).where(
        Organization.id == org_id,
        Organization.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    org = result.scalar_one_or_none()
    if org is None:
        return False

    org.deleted_at = datetime.now(timezone.utc)
    await db.flush()
    return True


async def count_orgs(db: AsyncSession) -> int:
    """Count active (non-deleted) organizations.

    Args:
        db: Async database session.

    Returns:
        Number of active organizations.
    """
    stmt = select(func.count()).select_from(Organization).where(
        Organization.deleted_at.is_(None),
    )
    return (await db.execute(stmt)).scalar_one()
