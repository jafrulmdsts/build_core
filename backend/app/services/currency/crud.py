"""Currency CRUD operations — low-level database access.

All queries filter out soft-deleted records (deleted_at IS NULL).
"""

from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.currency import Currency


async def get_currency_by_id(
    db: AsyncSession, currency_id: str
) -> Currency | None:
    """Fetch a single currency by ID.

    Args:
        db: Async database session.
        currency_id: UUID string of the currency.

    Returns:
        Currency row or None if not found / deleted.
    """
    stmt = select(Currency).where(
        Currency.id == currency_id,
        Currency.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_currency_by_code(
    db: AsyncSession, code: str
) -> Currency | None:
    """Fetch a single currency by its ISO code.

    Args:
        db: Async database session.
        code: ISO 4217 currency code (e.g. BDT, USD).

    Returns:
        Currency row or None if not found / deleted.
    """
    stmt = select(Currency).where(
        Currency.code == code,
        Currency.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def list_currencies(
    db: AsyncSession,
    page: int = 1,
    per_page: int = 20,
    is_active_only: bool = True,
) -> tuple[list[Currency], int]:
    """List currencies with pagination and optional active filter.

    Args:
        db: Async database session.
        page: 1-based page index.
        per_page: Items per page.
        is_active_only: If True, only return active currencies.

    Returns:
        Tuple of (items, total_count).
    """
    filters = [Currency.deleted_at.is_(None)]
    if is_active_only:
        filters.append(Currency.is_active.is_(True))

    # Count
    count_stmt = select(func.count()).select_from(Currency).where(*filters)
    total = (await db.execute(count_stmt)).scalar_one()

    # Fetch page
    offset = (page - 1) * per_page
    stmt = (
        select(Currency)
        .where(*filters)
        .order_by(Currency.created_at.asc())
        .offset(offset)
        .limit(per_page)
    )
    result = await db.execute(stmt)
    items = list(result.scalars().all())

    return items, total


async def create_currency(db: AsyncSession, **kwargs: object) -> Currency:
    """Create a new currency and flush to the session.

    Args:
        db: Async database session.
        **kwargs: Column values for the new Currency.

    Returns:
        The new Currency instance (id populated after flush).
    """
    currency = Currency(**kwargs)
    db.add(currency)
    await db.flush()
    return currency


async def update_currency(
    db: AsyncSession, currency_id: str, **kwargs: object
) -> Currency | None:
    """Update a currency by ID (excludes soft-deleted).

    Args:
        db: Async database session.
        currency_id: UUID string of the currency.
        **kwargs: Column values to update.

    Returns:
        Updated Currency row or None if not found.
    """
    stmt = select(Currency).where(
        Currency.id == currency_id,
        Currency.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    currency = result.scalar_one_or_none()
    if currency is None:
        return None

    for key, value in kwargs.items():
        if value is not None:
            setattr(currency, key, value)

    await db.flush()
    return currency


async def get_base_currency(db: AsyncSession) -> Currency | None:
    """Fetch the current base currency.

    Args:
        db: Async database session.

    Returns:
        Currency row marked as base currency, or None.
    """
    stmt = select(Currency).where(
        Currency.is_base_currency.is_(True),
        Currency.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()
