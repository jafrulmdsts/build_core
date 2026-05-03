"""
BuildCore Subscription Routes.

CRUD endpoints for managing subscription plans.
Create, update, and delete require super admin access.
List and get are available to all authenticated users.
"""

from fastapi import APIRouter, Depends

from app.core.exceptions import BuildCoreError
from app.core.responses import error_response, success_response
from app.core.dependencies import (
    get_current_user,
    require_super_admin,
    get_db_session,
)
from app.schemas.subscription import (
    SubscriptionPlanCreate,
    SubscriptionPlanUpdate,
)
from app.services.subscription.service import (
    get_plan,
    list_plans,
    create_plan,
    update_plan,
    delete_plan,
)

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])


@router.get("/")
async def list_plans_endpoint(
    include_inactive: bool = False,
    db=Depends(get_db_session),
    _current_user: dict = Depends(get_current_user),
):
    """List all subscription plans. Active only by default.
    Set ?include_inactive=true to see all plans (super admin).
    """
    try:
        plans = await list_plans(db, include_inactive=include_inactive)
        return success_response(data=plans, message="Subscription plans retrieved")
    except BuildCoreError as exc:
        return error_response(exc)


@router.get("/{plan_id}")
async def get_plan_endpoint(
    plan_id: str,
    db=Depends(get_db_session),
    _current_user: dict = Depends(get_current_user),
):
    """Retrieve a single subscription plan by ID."""
    try:
        plan = await get_plan(db, plan_id)
        return success_response(data=plan, message="Subscription plan retrieved")
    except BuildCoreError as exc:
        return error_response(exc)


@router.post("/", status_code=201)
async def create_plan_endpoint(
    body: SubscriptionPlanCreate,
    db=Depends(get_db_session),
    _current_user: dict = Depends(require_super_admin),
):
    """Create a new subscription plan. Super admin only."""
    try:
        plan = await create_plan(db, body)
        return success_response(data=plan, message="Subscription plan created",)
    except BuildCoreError as exc:
        return error_response(exc)


@router.put("/{plan_id}")
async def update_plan_endpoint(
    plan_id: str,
    body: SubscriptionPlanUpdate,
    db=Depends(get_db_session),
    _current_user: dict = Depends(require_super_admin),
):
    """Update an existing subscription plan. Super admin only."""
    try:
        plan = await update_plan(db, plan_id, body)
        return success_response(data=plan, message="Subscription plan updated")
    except BuildCoreError as exc:
        return error_response(exc)


@router.delete("/{plan_id}")
async def delete_plan_endpoint(
    plan_id: str,
    db=Depends(get_db_session),
    _current_user: dict = Depends(require_super_admin),
):
    """Soft-delete a subscription plan. Super admin only."""
    try:
        result = await delete_plan(db, plan_id)
        return success_response(data=result, message="Subscription plan deleted")
    except BuildCoreError as exc:
        return error_response(exc)
