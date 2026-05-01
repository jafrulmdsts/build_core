"""
BuildCore Currency Routes.

CRUD endpoints for managing currencies. Reference data endpoints
(except create/update) use minimal auth (get_current_user).
Create and update require super admin.
"""

from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user, require_super_admin, get_db_session
from app.core.exceptions import BuildCoreError
from app.core.pagination import get_pagination_params
from app.core.responses import error_response, paginated_response, success_response
from app.schemas.currency import CurrencyCreate, CurrencyUpdate
from app.services.currency.service import (
    create_currency as create_currency_svc,
    get_currency as get_currency_svc,
    list_currencies as list_currencies_svc,
    update_currency as update_currency_svc,
)

router = APIRouter(prefix="/currencies", tags=["Currencies"])


@router.get("/")
async def list_currencies_endpoint(
    db=Depends(get_db_session),
    pagination=Depends(get_pagination_params),
    _current_user: dict = Depends(get_current_user),
):
    """List all active currencies. Minimal auth required (reference data)."""
    try:
        result = await list_currencies_svc(
            db, page=pagination.page, per_page=pagination.per_page
        )
        return paginated_response(
            data=result["items"],
            page=result["page"],
            per_page=result["per_page"],
            total=result["total"],
            message="Currencies retrieved",
        )
    except BuildCoreError as exc:
        return error_response(exc)


@router.post("/")
async def create_currency_endpoint(
    body: CurrencyCreate,
    db=Depends(get_db_session),
    _current_user: dict = Depends(require_super_admin),
):
    """Create a new currency. Super admin only."""
    try:
        currency = await create_currency_svc(db, data=body)
        return success_response(data=currency, message="Currency created")
    except BuildCoreError as exc:
        return error_response(exc)


@router.get("/{currency_id}")
async def get_currency_endpoint(
    currency_id: str,
    db=Depends(get_db_session),
    _current_user: dict = Depends(get_current_user),
):
    """Retrieve a single currency by ID. Minimal auth required (reference data)."""
    try:
        currency = await get_currency_svc(db, currency_id=currency_id)
        return success_response(data=currency, message="Currency retrieved")
    except BuildCoreError as exc:
        return error_response(exc)


@router.put("/{currency_id}")
async def update_currency_endpoint(
    currency_id: str,
    body: CurrencyUpdate,
    db=Depends(get_db_session),
    _current_user: dict = Depends(require_super_admin),
):
    """Update an existing currency. Super admin only."""
    try:
        currency = await update_currency_svc(
            db, currency_id=currency_id, data=body
        )
        return success_response(data=currency, message="Currency updated")
    except BuildCoreError as exc:
        return error_response(exc)
