"""User CRUD operations — low-level database access.

All queries filter out soft-deleted records (deleted_at IS NULL).
"""

from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


async def get_user_by_id(db: AsyncSession, user_id: str) -> User | None:
    """Fetch a single user by ID (excludes soft-deleted).

    Args:
        db: Async database session.
        user_id: UUID string of the user.

    Returns:
        User row or None if not found / deleted.
    """
    stmt = select(User).where(
        User.id == user_id,
        User.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def list_users_by_org(
    db: AsyncSession,
    org_id: str,
    page: int = 1,
    per_page: int = 20,
) -> tuple[list[User], int]:
    """List users belonging to an organization with pagination.

    Args:
        db: Async database session.
        org_id: UUID string of the organization.
        page: 1-based page index.
        per_page: Items per page.

    Returns:
        Tuple of (items, total_count).
    """
    base_filter = (
        User.organization_id == org_id,
        User.deleted_at.is_(None),
    )

    # Count
    count_stmt = select(func.count()).select_from(User).where(*base_filter)
    total = (await db.execute(count_stmt)).scalar_one()

    # Fetch page
    offset = (page - 1) * per_page
    stmt = (
        select(User)
        .where(*base_filter)
        .order_by(User.created_at.desc())
        .offset(offset)
        .limit(per_page)
    )
    result = await db.execute(stmt)
    items = list(result.scalars().all())

    return items, total


async def update_user(
    db: AsyncSession,
    user_id: str,
    **kwargs: object,
) -> User | None:
    """Update a user by ID (excludes soft-deleted).

    Args:
        db: Async database session.
        user_id: UUID string of the user.
        **kwargs: Column values to update.

    Returns:
        Updated User row or None if not found.
    """
    stmt = select(User).where(
        User.id == user_id,
        User.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if user is None:
        return None

    for key, value in kwargs.items():
        if value is not None:
            setattr(user, key, value)

    await db.flush()
    return user


async def delete_user(db: AsyncSession, user_id: str) -> bool:
    """Soft-delete a user by setting deleted_at.

    Args:
        db: Async database session.
        user_id: UUID string of the user.

    Returns:
        True if the user was found and soft-deleted, False otherwise.
    """
    stmt = select(User).where(
        User.id == user_id,
        User.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if user is None:
        return False

    user.deleted_at = datetime.now(timezone.utc)
    await db.flush()
    return True
