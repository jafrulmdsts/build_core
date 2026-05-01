"""Subscription plan CRUD operations — low-level database access.

All queries filter out soft-deleted records (deleted_at IS NULL).
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.subscription import SubscriptionPlan


async def get_plan_by_id(db: AsyncSession, plan_id: str) -> SubscriptionPlan | None:
    """Fetch a single subscription plan by ID (excludes soft-deleted).

    Args:
        db: Async database session.
        plan_id: UUID string of the plan.

    Returns:
        SubscriptionPlan row or None if not found / deleted.
    """
    stmt = select(SubscriptionPlan).where(
        SubscriptionPlan.id == plan_id,
        SubscriptionPlan.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_plan_by_slug(db: AsyncSession, slug: str) -> SubscriptionPlan | None:
    """Fetch a single subscription plan by slug (excludes soft-deleted).

    Args:
        db: Async database session.
        slug: URL-friendly slug string.

    Returns:
        SubscriptionPlan row or None if not found / deleted.
    """
    stmt = select(SubscriptionPlan).where(
        SubscriptionPlan.slug == slug,
        SubscriptionPlan.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def list_plans(db: AsyncSession) -> list[SubscriptionPlan]:
    """List all active subscription plans (excludes soft-deleted and inactive).

    Args:
        db: Async database session.

    Returns:
        List of active SubscriptionPlan rows.
    """
    stmt = (
        select(SubscriptionPlan)
        .where(
            SubscriptionPlan.deleted_at.is_(None),
            SubscriptionPlan.is_active.is_(True),
        )
        .order_by(SubscriptionPlan.price_monthly.asc())
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())
