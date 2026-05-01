"""
Seed default subscription plans.

Creates the initial pricing tiers available for organizations:
Trial (free), Basic ($29/mo), and Premium ($99/mo).
"""

import json

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.subscription import SubscriptionPlan

DEFAULT_PLANS: list[dict] = [
    {
        "id": "00000000-0000-4000-c000-000000000001",
        "name": "Trial",
        "slug": "trial",
        "description": "Free trial plan for new organizations to explore BuildCore features.",
        "price_monthly": 0,
        "price_yearly": 0,
        "max_users": 3,
        "max_projects": 2,
        "max_storage_mb": 500,
        "features": json.dumps([
            "Up to 3 users",
            "Up to 2 projects",
            "500 MB storage",
            "Basic expense tracking",
            "Email support",
        ]),
        "trial_days": 30,
        "is_active": True,
    },
    {
        "id": "00000000-0000-4000-c000-000000000002",
        "name": "Basic",
        "slug": "basic",
        "description": "Affordable plan for small construction teams getting started.",
        "price_monthly": 29.00,
        "price_yearly": 290.00,
        "max_users": 10,
        "max_projects": 20,
        "max_storage_mb": 5000,
        "features": json.dumps([
            "Up to 10 users",
            "Up to 20 projects",
            "5 GB storage",
            "Full expense management",
            "Project & employee management",
            "Contractor management",
            "Basic reports",
            "Priority email support",
        ]),
        "trial_days": None,
        "is_active": True,
    },
    {
        "id": "00000000-0000-4000-c000-000000000003",
        "name": "Premium",
        "slug": "premium",
        "description": "Full-featured plan for growing construction businesses.",
        "price_monthly": 99.00,
        "price_yearly": 990.00,
        "max_users": 100,
        "max_projects": None,
        "max_storage_mb": 50000,
        "features": json.dumps([
            "Up to 100 users",
            "Unlimited projects",
            "50 GB storage",
            "Full expense management with approvals",
            "Advanced reporting & export",
            "Audit trail",
            "Role-based access control",
            "Custom permissions",
            "Dedicated support",
        ]),
        "trial_days": None,
        "is_active": True,
    },
]


async def seed_subscription_plans(db: AsyncSession) -> None:
    """Insert default subscription plans if they don't already exist.

    Args:
        db: Active async database session.
    """
    for plan_data in DEFAULT_PLANS:
        stmt = select(SubscriptionPlan).where(SubscriptionPlan.id == plan_data["id"])
        result = await db.execute(stmt)
        if result.scalar_one_or_none() is None:
            db.add(SubscriptionPlan(**plan_data))
    await db.flush()
