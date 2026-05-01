"""
BuildCore Contractor Routes.

CRUD endpoints for managing contractors, their contracts, and payments.
Tenant context required for all operations.
"""

from fastapi import APIRouter, Depends

from app.core.exceptions import BuildCoreError
from app.core.pagination import get_pagination_params
from app.core.responses import error_response, paginated_response, success_response
from app.core.dependencies import require_tenant, require_super_admin, get_db_session
from app.schemas.contractor import (
    ContractorCreate,
    ContractorUpdate,
    ContractCreate,
    ContractUpdate,
    PaymentCreate,
    PaymentUpdate,
)
from app.services.contractor.service import (
    get_contractor as svc_get_contractor,
    list_contractors as svc_list_contractors,
    create_contractor as svc_create_contractor,
    update_contractor as svc_update_contractor,
    delete_contractor as svc_delete_contractor,
    get_contract as svc_get_contract,
    list_contracts as svc_list_contracts,
    create_contract as svc_create_contract,
    update_contract as svc_update_contract,
    list_payments as svc_list_payments,
    create_payment as svc_create_payment,
    update_payment as svc_update_payment,
)

router = APIRouter(prefix="/contractors", tags=["Contractors"])


# ---------------------------------------------------------------------------
# Contractor CRUD
# ---------------------------------------------------------------------------


@router.get("/")
async def list_contractors_endpoint(
    db=Depends(get_db_session),
    pagination=Depends(get_pagination_params),
    current_user: dict = Depends(require_tenant),
):
    """List all contractors for the tenant organization. Supports pagination."""
    try:
        org_id = current_user.get("organization_id")
        result = await svc_list_contractors(
            db, org_id=org_id, page=pagination.page, per_page=pagination.per_page
        )
        return paginated_response(
            data=result["items"],
            page=result["page"],
            per_page=result["per_page"],
            total=result["total"],
            message="Contractors retrieved",
        )
    except BuildCoreError as exc:
        return error_response(exc)


@router.post("/")
async def create_contractor_endpoint(
    body: ContractorCreate,
    db=Depends(get_db_session),
    current_user: dict = Depends(require_tenant),
):
    """Create a new contractor. Requires tenant context."""
    try:
        org_id = current_user.get("organization_id")
        user_id = current_user.get("sub")
        ctr = await svc_create_contractor(db, org_id=org_id, data=body, created_by=user_id)
        return success_response(data=ctr, message="Contractor created", meta={"status_code": 201})
    except BuildCoreError as exc:
        return error_response(exc)


@router.get("/{ctr_id}")
async def get_contractor_endpoint(
    ctr_id: str,
    db=Depends(get_db_session),
    current_user: dict = Depends(require_tenant),
):
    """Retrieve a single contractor by ID. Requires tenant context."""
    try:
        org_id = current_user.get("organization_id")
        ctr = await svc_get_contractor(db, org_id=org_id, ctr_id=ctr_id)
        return success_response(data=ctr, message="Contractor retrieved")
    except BuildCoreError as exc:
        return error_response(exc)


@router.put("/{ctr_id}")
async def update_contractor_endpoint(
    ctr_id: str,
    body: ContractorUpdate,
    db=Depends(get_db_session),
    current_user: dict = Depends(require_tenant),
):
    """Update an existing contractor. Requires tenant context."""
    try:
        org_id = current_user.get("organization_id")
        ctr = await svc_update_contractor(db, org_id=org_id, ctr_id=ctr_id, data=body)
        return success_response(data=ctr, message="Contractor updated")
    except BuildCoreError as exc:
        return error_response(exc)


@router.delete("/{ctr_id}")
async def delete_contractor_endpoint(
    ctr_id: str,
    db=Depends(get_db_session),
    _current_user: dict = Depends(require_super_admin),
):
    """Soft-delete a contractor. Super admin only."""
    try:
        from app.services.contractor import crud
        ctr = await crud.get_contractor_by_id(db, ctr_id)
        if ctr is None:
            from app.core.exceptions import NotFoundError
            raise NotFoundError(message="Contractor not found")
        await svc_delete_contractor(db, org_id=ctr.organization_id, ctr_id=ctr_id)
        return success_response(message="Contractor deleted")
    except BuildCoreError as exc:
        return error_response(exc)


# ---------------------------------------------------------------------------
# Contract CRUD (nested under contractor)
# ---------------------------------------------------------------------------


@router.get("/{ctr_id}/contracts")
async def list_contracts_endpoint(
    ctr_id: str,
    db=Depends(get_db_session),
    pagination=Depends(get_pagination_params),
    current_user: dict = Depends(require_tenant),
):
    """List contracts for a specific contractor. Supports pagination."""
    try:
        org_id = current_user.get("organization_id")
        result = await svc_list_contracts(
            db, org_id=org_id, contractor_id=ctr_id,
            page=pagination.page, per_page=pagination.per_page,
        )
        return paginated_response(
            data=result["items"],
            page=result["page"],
            per_page=result["per_page"],
            total=result["total"],
            message="Contracts retrieved",
        )
    except BuildCoreError as exc:
        return error_response(exc)


@router.post("/{ctr_id}/contracts")
async def create_contract_endpoint(
    ctr_id: str,
    body: ContractCreate,
    db=Depends(get_db_session),
    current_user: dict = Depends(require_tenant),
):
    """Create a new contract for a contractor. Requires tenant context."""
    try:
        org_id = current_user.get("organization_id")
        user_id = current_user.get("sub")
        contract = await svc_create_contract(
            db, org_id=org_id, contractor_id=ctr_id, data=body, created_by=user_id
        )
        return success_response(
            data=contract, message="Contract created", meta={"status_code": 201}
        )
    except BuildCoreError as exc:
        return error_response(exc)


@router.get("/contracts/{contract_id}")
async def get_contract_endpoint(
    contract_id: str,
    db=Depends(get_db_session),
    current_user: dict = Depends(require_tenant),
):
    """Retrieve a single contract by ID. Requires tenant context."""
    try:
        org_id = current_user.get("organization_id")
        contract = await svc_get_contract(db, org_id=org_id, contract_id=contract_id)
        return success_response(data=contract, message="Contract retrieved")
    except BuildCoreError as exc:
        return error_response(exc)


@router.put("/contracts/{contract_id}")
async def update_contract_endpoint(
    contract_id: str,
    body: ContractUpdate,
    db=Depends(get_db_session),
    current_user: dict = Depends(require_tenant),
):
    """Update an existing contract. Requires tenant context."""
    try:
        org_id = current_user.get("organization_id")
        contract = await svc_update_contract(
            db, org_id=org_id, contract_id=contract_id, data=body
        )
        return success_response(data=contract, message="Contract updated")
    except BuildCoreError as exc:
        return error_response(exc)


# ---------------------------------------------------------------------------
# Payment CRUD (nested under contract)
# ---------------------------------------------------------------------------


@router.get("/contracts/{contract_id}/payments")
async def list_payments_endpoint(
    contract_id: str,
    db=Depends(get_db_session),
    pagination=Depends(get_pagination_params),
    current_user: dict = Depends(require_tenant),
):
    """List payments for a specific contract. Supports pagination."""
    try:
        org_id = current_user.get("organization_id")
        result = await svc_list_payments(
            db, org_id=org_id, contract_id=contract_id,
            page=pagination.page, per_page=pagination.per_page,
        )
        return paginated_response(
            data=result["items"],
            page=result["page"],
            per_page=result["per_page"],
            total=result["total"],
            message="Payments retrieved",
        )
    except BuildCoreError as exc:
        return error_response(exc)


@router.post("/contracts/{contract_id}/payments")
async def create_payment_endpoint(
    contract_id: str,
    body: PaymentCreate,
    db=Depends(get_db_session),
    current_user: dict = Depends(require_tenant),
):
    """Create a new payment for a contract. Requires tenant context."""
    try:
        org_id = current_user.get("organization_id")
        user_id = current_user.get("sub")
        payment = await svc_create_payment(
            db, org_id=org_id, contract_id=contract_id, data=body, created_by=user_id
        )
        return success_response(
            data=payment, message="Payment created", meta={"status_code": 201}
        )
    except BuildCoreError as exc:
        return error_response(exc)
