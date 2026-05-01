"""Location CRUD operations — low-level database access.

All queries filter out soft-deleted records (deleted_at IS NULL)
and active records (is_active = True) by default.
"""

from datetime import datetime, timezone
from typing import Any, Type

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.location import (
    Country,
    District,
    Division,
    PostOffice,
    Upazila,
)

# Type alias for any location model class
LocationModel = Type[Country | Division | District | Upazila | PostOffice]


# ---------------------------------------------------------------------------
# List queries (active + not deleted)
# ---------------------------------------------------------------------------


async def get_countries(db: AsyncSession) -> list[Country]:
    """Fetch all active, non-deleted countries.

    Args:
        db: Async database session.

    Returns:
        List of Country rows ordered by name.
    """
    stmt = (
        select(Country)
        .where(
            Country.deleted_at.is_(None),
            Country.is_active.is_(True),
        )
        .order_by(Country.name.asc())
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_divisions_by_country(
    db: AsyncSession,
    country_id: str,
) -> list[Division]:
    """Fetch active divisions for a given country.

    Args:
        db: Async database session.
        country_id: UUID string of the parent country.

    Returns:
        List of Division rows ordered by name.
    """
    stmt = (
        select(Division)
        .where(
            Division.country_id == country_id,
            Division.deleted_at.is_(None),
            Division.is_active.is_(True),
        )
        .order_by(Division.name.asc())
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_districts_by_division(
    db: AsyncSession,
    division_id: str,
) -> list[District]:
    """Fetch active districts for a given division.

    Args:
        db: Async database session.
        division_id: UUID string of the parent division.

    Returns:
        List of District rows ordered by name.
    """
    stmt = (
        select(District)
        .where(
            District.division_id == division_id,
            District.deleted_at.is_(None),
            District.is_active.is_(True),
        )
        .order_by(District.name.asc())
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_upazilas_by_district(
    db: AsyncSession,
    district_id: str,
) -> list[Upazila]:
    """Fetch active upazilas for a given district.

    Args:
        db: Async database session.
        district_id: UUID string of the parent district.

    Returns:
        List of Upazila rows ordered by name.
    """
    stmt = (
        select(Upazila)
        .where(
            Upazila.district_id == district_id,
            Upazila.deleted_at.is_(None),
            Upazila.is_active.is_(True),
        )
        .order_by(Upazila.name.asc())
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_post_offices_by_upazila(
    db: AsyncSession,
    upazila_id: str,
) -> list[PostOffice]:
    """Fetch active post offices for a given upazila.

    Args:
        db: Async database session.
        upazila_id: UUID string of the parent upazila.

    Returns:
        List of PostOffice rows ordered by name.
    """
    stmt = (
        select(PostOffice)
        .where(
            PostOffice.upazila_id == upazila_id,
            PostOffice.deleted_at.is_(None),
            PostOffice.is_active.is_(True),
        )
        .order_by(PostOffice.name.asc())
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


# ---------------------------------------------------------------------------
# Generic CRUD operations
# ---------------------------------------------------------------------------


async def get_location_entity(
    db: AsyncSession,
    table_class: LocationModel,
    entity_id: str,
) -> Any:
    """Fetch a single location entity by ID (excludes soft-deleted).

    Args:
        db: Async database session.
        table_class: SQLAlchemy model class (e.g. Country, Division).
        entity_id: UUID string of the entity.

    Returns:
        Model instance or None if not found / deleted.
    """
    stmt = select(table_class).where(
        table_class.id == entity_id,
        table_class.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create_location_entity(
    db: AsyncSession,
    table_class: LocationModel,
    **kwargs: Any,
) -> Any:
    """Create a new location entity and flush to the session.

    Args:
        db: Async database session.
        table_class: SQLAlchemy model class to instantiate.
        **kwargs: Column values for the new entity.

    Returns:
        The new entity instance (id populated after flush).
    """
    entity = table_class(**kwargs)
    db.add(entity)
    await db.flush()
    return entity


async def update_location_entity(
    db: AsyncSession,
    table_class: LocationModel,
    entity_id: str,
    **kwargs: Any,
) -> Any | None:
    """Update a location entity by ID (excludes soft-deleted).

    Args:
        db: Async database session.
        table_class: SQLAlchemy model class.
        entity_id: UUID string of the entity.
        **kwargs: Column values to update.

    Returns:
        Updated entity or None if not found.
    """
    entity = await get_location_entity(db, table_class, entity_id)
    if entity is None:
        return None

    for key, value in kwargs.items():
        if value is not None:
            setattr(entity, key, value)

    await db.flush()
    return entity


async def delete_location_entity(
    db: AsyncSession,
    table_class: LocationModel,
    entity_id: str,
) -> bool:
    """Soft-delete a location entity by setting deleted_at.

    Args:
        db: Async database session.
        table_class: SQLAlchemy model class.
        entity_id: UUID string of the entity.

    Returns:
        True if the entity was found and soft-deleted, False otherwise.
    """
    entity = await get_location_entity(db, table_class, entity_id)
    if entity is None:
        return False

    entity.deleted_at = datetime.now(timezone.utc)
    await db.flush()
    return True
