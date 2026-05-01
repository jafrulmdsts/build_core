"""Subscription plan service layer — business logic.

Returns Pydantic response schemas with parsed features.
"""

import json
from decimal import Decimal

from app.core.exceptions import NotFoundError
from app.schemas.subscription import SubscriptionPlanResponse
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


async def get_plan(db, plan_id: str) -> SubscriptionPlanResponse:
    """Get a subscription plan by ID.

    Args:
        db: Async database session.
        plan_id: UUID string of the plan.

    Returns:
        SubscriptionPlanResponse schema.

    Raises:
        NotFoundError: If the plan does not exist.
    """
    plan = await crud.get_plan_by_id(db, plan_id)
    if plan is None:
        raise NotFoundError(message="Subscription plan not found")

    data = SubscriptionPlanResponse.model_validate(plan)
    data.features = _parse_features(plan.features)
    return data


async def list_plans(db) -> list[SubscriptionPlanResponse]:
    """List all active subscription plans.

    Args:
        db: Async database session.

    Returns:
        List of SubscriptionPlanResponse schemas.
    """
    plans = await crud.list_plans(db)
    result = []
    for plan in plans:
        data = SubscriptionPlanResponse.model_validate(plan)
        data.features = _parse_features(plan.features)
        result.append(data)
    return result
