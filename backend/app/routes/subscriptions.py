"""
BuildCore Subscription Routes.

Read-only endpoints for viewing available subscription plans.
"""

from fastapi import APIRouter, Depends

from app.core.exceptions import BuildCoreError
from app.core.responses import error_response, success_response
from app.core.dependencies import get_current_user, get_db_session
from app.services.subscription.service import get_plan, list_plans

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])


@router.get("/")
async def list_plans_endpoint(
    db=Depends(get_db_session),
    _current_user: dict = Depends(get_current_user),
):
    """List all active subscription plans. Requires authentication."""
    try:
        plans = await list_plans(db)
        return success_response(data=plans, message="Subscription plans retrieved")
    except BuildCoreError as exc:
        return error_response(exc)


@router.get("/{plan_id}")
async def get_plan_endpoint(
    plan_id: str,
    db=Depends(get_db_session),
    _current_user: dict = Depends(get_current_user),
):
    """Retrieve a single subscription plan by ID. Requires authentication."""
    try:
        plan = await get_plan(db, plan_id)
        return success_response(data=plan, message="Subscription plan retrieved")
    except BuildCoreError as exc:
        return error_response(exc)
