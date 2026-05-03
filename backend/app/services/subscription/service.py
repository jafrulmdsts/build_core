"""Subscription plan service layer — business logic.

Returns Pydantic response schemas with parsed features.
"""

import json
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ConflictError
from app.schemas.subscription import (
    SubscriptionPlanCreate,
    SubscriptionPlanResponse,
    SubscriptionPlanUpdate,
)
from app.services.subscription import crud


def _parse_features(features_text: str | None) -> list[str]:
    """Safely parse a JSON-encoded features string into a list."""
    if not features_text:
        return []
    try:
        parsed = json.loads(features_text)
        if isinstance(parsed, list):
            return [str(f) for f in parsed]
        return []
    except (json.JSONDecodeError, TypeError):
        return []


def _to_response(plan) -> SubscriptionPlanResponse:
    """Convert a SubscriptionPlan ORM model to a response schema.

    Builds the response manually instead of using model_validate because
    the ORM ``features`` column stores a JSON string while the schema
    expects ``list[str]``.  model_validate would raise a ValidationError
    on the type mismatch *before* we get a chance to parse it.
    """
    return SubscriptionPlanResponse(
        id=plan.id,
        name=plan.name,
        slug=plan.slug,
        description=plan.description,
        price_monthly=plan.price_monthly,
        price_yearly=plan.price_yearly,
        max_users=plan.max_users,
        max_projects=plan.max_projects,
        max_storage_mb=plan.max_storage_mb,
        features=_parse_features(plan.features),
        trial_days=plan.trial_days,
        is_active=plan.is_active,
        created_at=plan.created_at,
        updated_at=plan.updated_at,
    )


async def get_plan(db: AsyncSession, plan_id: str) -> SubscriptionPlanResponse:
    """Get a subscription plan by ID."""
    plan = await crud.get_plan_by_id(db, plan_id)
    if plan is None:
        raise NotFoundError(message="Subscription plan not found")
    return _to_response(plan)


async def list_plans(
    db: AsyncSession, include_inactive: bool = False
) -> list[SubscriptionPlanResponse]:
    """List subscription plans.

    Args:
        db: Async database session.
        include_inactive: If True, return all plans; otherwise only active.
    """
    plans = await crud.list_plans(db, include_inactive=include_inactive)
    return [_to_response(p) for p in plans]


async def create_plan(db: AsyncSession, data: SubscriptionPlanCreate) -> SubscriptionPlanResponse:
    """Create a new subscription plan.

    Validates slug uniqueness before creation.
    """
    existing = await crud.get_plan_by_slug(db, data.slug)
    if existing is not None:
        raise ConflictError(
            message=f"Subscription plan with slug '{data.slug}' already exists",
            details={"field": "slug"},
        )

    plan = await crud.create_plan(
        db,
        name=data.name,
        slug=data.slug,
        description=data.description,
        price_monthly=data.price_monthly,
        price_yearly=data.price_yearly,
        max_users=data.max_users,
        max_projects=data.max_projects,
        max_storage_mb=data.max_storage_mb,
        features=data.features,
        trial_days=data.trial_days,
        is_active=data.is_active,
    )
    return _to_response(plan)


async def update_plan(
    db: AsyncSession, plan_id: str, data: SubscriptionPlanUpdate
) -> SubscriptionPlanResponse:
    """Update an existing subscription plan.

    Validates slug uniqueness if slug is being changed.
    """
    plan = await crud.get_plan_by_id(db, plan_id)
    if plan is None:
        raise NotFoundError(message="Subscription plan not found")

    update_fields = data.model_dump(exclude_unset=True)

    # Check slug uniqueness if slug is being updated
    if "slug" in update_fields and update_fields["slug"] != plan.slug:
        existing = await crud.get_plan_by_slug(db, update_fields["slug"])
        if existing is not None:
            raise ConflictError(
                message=f"Subscription plan with slug '{update_fields['slug']}' already exists",
                details={"field": "slug"},
            )

    await crud.update_plan(db, plan, **update_fields)
    return _to_response(plan)


async def delete_plan(db: AsyncSession, plan_id: str) -> dict:
    """Soft-delete a subscription plan."""
    deleted = await crud.soft_delete_plan(db, plan_id)
    if not deleted:
        raise NotFoundError(message="Subscription plan not found")
    return {"message": "Subscription plan deleted"}
