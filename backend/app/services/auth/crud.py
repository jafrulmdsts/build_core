"""
Auth CRUD operations.

Low-level database queries for user entities. All queries filter
out soft-deleted rows (deleted_at IS NULL).
"""

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


# ---------------------------------------------------------------------------
# Read queries
# ---------------------------------------------------------------------------


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    """Fetch a non-deleted user by email address.

    Args:
        db: Async database session.
        email: Case-insensitive unique email to look up.

    Returns:
        User instance or None if not found / deleted.
    """
    stmt = select(User).where(
        User.email == email,
        User.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: str) -> User | None:
    """Fetch a non-deleted user by primary-key id.

    Args:
        db: Async database session.
        user_id: UUID string (36 chars).

    Returns:
        User instance or None if not found / deleted.
    """
    stmt = select(User).where(
        User.id == user_id,
        User.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_by_invite_token(db: AsyncSession, token: str) -> User | None:
    """Fetch a non-deleted user by invite token.

    Args:
        db: Async database session.
        token: Invite token string.

    Returns:
        User instance or None if not found / deleted.
    """
    stmt = select(User).where(
        User.invite_token == token,
        User.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


# ---------------------------------------------------------------------------
# Mutations
# ---------------------------------------------------------------------------


async def create_user(db: AsyncSession, **kwargs) -> User:
    """Insert a new user row and flush to the session.

    The caller must commit (or let the request handler commit) after this.

    Args:
        db: Async database session.
        **kwargs: Column values forwarded to the User constructor.

    Returns:
        The newly created User instance (with id populated).
    """
    user = User(**kwargs)
    db.add(user)
    await db.flush()
    return user


async def update_user(db: AsyncSession, user_id: str, **kwargs) -> User:
    """Update fields on an existing user and return the refreshed instance.

    Args:
        db: Async database session.
        user_id: UUID string of the user to update.
        **kwargs: Column name -> value pairs to update.

    Returns:
        The updated User instance.

    Raises:
        NotFoundError: Implicitly if user does not exist (caller handles).
    """
    await db.execute(
        update(User)
        .where(User.id == user_id, User.deleted_at.is_(None))
        .values(**kwargs)
    )
    await db.flush()

    # Return the refreshed instance
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    return result.scalar_one()


# ---------------------------------------------------------------------------
# Paginated list
# ---------------------------------------------------------------------------


async def get_users_by_org(
    db: AsyncSession,
    org_id: str,
    page: int = 1,
    per_page: int = 20,
) -> tuple[list[User], int]:
    """Return a paginated list of non-deleted users for an organization.

    Args:
        db: Async database session.
        org_id: Organization UUID string.
        page: 1-based page index.
        per_page: Number of items per page.

    Returns:
        Tuple of (users list, total_count).
    """
    base_filter = (
        User.organization_id == org_id,
        User.deleted_at.is_(None),
    )

    # Total count
    count_stmt = select(func.count()).select_from(User).where(*base_filter)
    total = (await db.execute(count_stmt)).scalar_one()

    # Paginated rows
    offset = (page - 1) * per_page
    list_stmt = (
        select(User)
        .where(*base_filter)
        .order_by(User.created_at.desc())
        .offset(offset)
        .limit(per_page)
    )
    result = await db.execute(list_stmt)
    users = list(result.scalars().all())

    return users, total
