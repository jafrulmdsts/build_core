"""Subscription plan CRUD operations — low-level database access.

All queries filter out soft-deleted records (deleted_at IS NULL).
"""

import json
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.subscription import SubscriptionPlan


async def get_plan_by_id(db: AsyncSession, plan_id: str) -> SubscriptionPlan | None:
    """Fetch a single subscription plan by ID (excludes soft-deleted)."""
    stmt = select(SubscriptionPlan).where(
        SubscriptionPlan.id == plan_id,
        SubscriptionPlan.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_plan_by_slug(db: AsyncSession, slug: str) -> SubscriptionPlan | None:
    """Fetch a single subscription plan by slug (excludes soft-deleted)."""
    stmt = select(SubscriptionPlan).where(
        SubscriptionPlan.slug == slug,
        SubscriptionPlan.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def list_plans(db: AsyncSession, include_inactive: bool = False) -> list[SubscriptionPlan]:
    """List subscription plans (excludes soft-deleted).

    Args:
        db: Async database session.
        include_inactive: If True, return all plans; otherwise only active ones.
    """
    stmt = select(SubscriptionPlan).where(
        SubscriptionPlan.deleted_at.is_(None),
    )
    if not include_inactive:
        stmt = stmt.where(SubscriptionPlan.is_active.is_(True))
    stmt = stmt.order_by(SubscriptionPlan.price_monthly.asc())
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def create_plan(db: AsyncSession, **kwargs) -> SubscriptionPlan:
    """Create a new subscription plan.

    Args:
        db: Async database session.
        **kwargs: Column values matching SubscriptionPlan fields.

    Returns:
        The created SubscriptionPlan instance (not yet committed).
    """
    # Serialize features list to JSON text
    features = kwargs.pop("features", [])
    if isinstance(features, list):
        features = json.dumps(features)

    plan = SubscriptionPlan(features=features, **kwargs)
    db.add(plan)
    await db.flush()
    await db.refresh(plan)
    return plan


async def update_plan(db: AsyncSession, plan: SubscriptionPlan, **kwargs) -> SubscriptionPlan:
    """Update an existing subscription plan.

    Args:
        db: Async database session.
        plan: The SubscriptionPlan instance to update.
        **kwargs: Column values to update.

    Returns:
        The updated SubscriptionPlan instance (not yet committed).
    """
    # Serialize features list to JSON text if provided
    features = kwargs.pop("features", None)
    if features is not None:
        if isinstance(features, list):
            kwargs["features"] = json.dumps(features)
        else:
            kwargs["features"] = features

    for key, value in kwargs.items():
        if value is not None:
            setattr(plan, key, value)

    await db.flush()
    await db.refresh(plan)
    return plan


async def soft_delete_plan(db: AsyncSession, plan_id: str) -> bool:
    """Soft-delete a subscription plan by setting deleted_at.

    Args:
        db: Async database session.
        plan_id: UUID string of the plan.

    Returns:
        True if deleted, False if not found.
    """
    plan = await get_plan_by_id(db, plan_id)
    if plan is None:
        return False

    from datetime import datetime, timezone
    plan.deleted_at = datetime.now(timezone.utc)
    await db.flush()
    return True
