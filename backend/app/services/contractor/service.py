"""Contractor service layer — business logic and validation.

Handles code generation, ownership scoping, and returns
Pydantic response schemas for contractors, contracts, and payments.
"""

from app.core.exceptions import NotFoundError
from app.schemas.contractor import (
    ContractorCreate,
    ContractorResponse,
    ContractorUpdate,
    ContractCreate,
    ContractResponse,
    ContractUpdate,
    PaymentCreate,
    PaymentResponse,
    PaymentUpdate,
)
from app.services.contractor import crud


# ---------------------------------------------------------------------------
# Contractor operations
# ---------------------------------------------------------------------------


async def get_contractor(db, org_id: str, ctr_id: str) -> ContractorResponse:
    """Get a single contractor by ID.

    Raises:
        NotFoundError: If the contractor does not exist or belongs to
            a different organization.
    """
    ctr = await crud.get_contractor_by_id(db, ctr_id)
    if ctr is None or ctr.organization_id != org_id:
        raise NotFoundError(message="Contractor not found")
    return ContractorResponse.model_validate(ctr)


async def list_contractors(
    db,
    org_id: str,
    page: int = 1,
    per_page: int = 20,
) -> dict:
    """List contractors for an organization with pagination."""
    items, total = await crud.list_contractors_by_org(db, org_id, page, per_page)
    total_pages = (total + per_page - 1) // per_page if per_page > 0 else 0
    return {
        "items": [ContractorResponse.model_validate(c) for c in items],
        "page": page,
        "per_page": per_page,
        "total": total,
        "total_pages": total_pages,
    }


async def create_contractor(
    db,
    org_id: str,
    data: ContractorCreate,
    created_by: str | None = None,
) -> ContractorResponse:
    """Create a new contractor with auto-generated contractor code."""
    count = await crud.count_contractors_by_org(db, org_id)
    contractor_code = f"CTR-{count + 1}"

    ctr = await crud.create_contractor(
        db,
        organization_id=org_id,
        contractor_code=contractor_code,
        name=data.name,
        phone=data.phone,
        email=data.email,
        address=data.address,
        nid_number=data.nid_number,
        trade_license=data.trade_license,
        bank_account=data.bank_account,
        notes=data.notes,
        created_by=created_by,
    )
    await db.refresh(ctr)
    return ContractorResponse.model_validate(ctr)


async def update_contractor(
    db,
    org_id: str,
    ctr_id: str,
    data: ContractorUpdate,
) -> ContractorResponse:
    """Update an existing contractor.

    Raises:
        NotFoundError: If the contractor does not exist.
    """
    ctr = await crud.get_contractor_by_id(db, ctr_id)
    if ctr is None or ctr.organization_id != org_id:
        raise NotFoundError(message="Contractor not found")

    update_data = data.model_dump(exclude_unset=True)
    updated = await crud.update_contractor(db, ctr_id, **update_data)
    await db.refresh(updated)
    return ContractorResponse.model_validate(updated)


async def delete_contractor(db, org_id: str, ctr_id: str) -> None:
    """Soft-delete a contractor.

    Raises:
        NotFoundError: If the contractor does not exist.
    """
    ctr = await crud.get_contractor_by_id(db, ctr_id)
    if ctr is None or ctr.organization_id != org_id:
        raise NotFoundError(message="Contractor not found")

    deleted = await crud.delete_contractor(db, ctr_id)
    if not deleted:
        raise NotFoundError(message="Contractor not found")


# ---------------------------------------------------------------------------
# Contract operations
# ---------------------------------------------------------------------------


async def get_contract(db, org_id: str, contract_id: str) -> ContractResponse:
    """Get a single contract by ID.

    Raises:
        NotFoundError: If the contract does not exist or belongs to
            a different organization.
    """
    contract = await crud.get_contract_by_id(db, contract_id)
    if contract is None or contract.organization_id != org_id:
        raise NotFoundError(message="Contract not found")
    return ContractResponse.model_validate(contract)


async def list_contracts(
    db,
    org_id: str,
    contractor_id: str,
    page: int = 1,
    per_page: int = 20,
) -> dict:
    """List contracts for a contractor with pagination.

    Raises:
        NotFoundError: If the contractor does not exist.
    """
    ctr = await crud.get_contractor_by_id(db, contractor_id)
    if ctr is None or ctr.organization_id != org_id:
        raise NotFoundError(message="Contractor not found")

    items, total = await crud.list_contracts_by_contractor(
        db, org_id, contractor_id, page, per_page
    )
    total_pages = (total + per_page - 1) // per_page if per_page > 0 else 0
    return {
        "items": [ContractResponse.model_validate(c) for c in items],
        "page": page,
        "per_page": per_page,
        "total": total,
        "total_pages": total_pages,
    }


async def create_contract(
    db,
    org_id: str,
    contractor_id: str,
    data: ContractCreate,
    created_by: str | None = None,
) -> ContractResponse:
    """Create a new contract for a contractor.

    Raises:
        NotFoundError: If the contractor does not exist.
    """
    ctr = await crud.get_contractor_by_id(db, contractor_id)
    if ctr is None or ctr.organization_id != org_id:
        raise NotFoundError(message="Contractor not found")

    count = await crud.count_contracts_by_org(db, org_id)
    contract_code = f"CC-{count + 1}"

    contract = await crud.create_contract(
        db,
        organization_id=org_id,
        contractor_id=contractor_id,
        project_id=data.project_id,
        contract_code=contract_code,
        title=data.title,
        description=data.description,
        work_scope=data.work_scope,
        total_amount=data.total_amount,
        currency_code=data.currency_code,
        start_date=data.start_date,
        end_date=data.end_date,
        payment_terms=data.payment_terms,
        status=data.status,
        notes=data.notes,
        created_by=created_by,
    )
    await db.refresh(contract)
    return ContractResponse.model_validate(contract)


async def update_contract(
    db,
    org_id: str,
    contract_id: str,
    data: ContractUpdate,
) -> ContractResponse:
    """Update an existing contract.

    Raises:
        NotFoundError: If the contract does not exist.
    """
    contract = await crud.get_contract_by_id(db, contract_id)
    if contract is None or contract.organization_id != org_id:
        raise NotFoundError(message="Contract not found")

    update_data = data.model_dump(exclude_unset=True)
    updated = await crud.update_contract(db, contract_id, **update_data)
    await db.refresh(updated)
    return ContractResponse.model_validate(updated)


# ---------------------------------------------------------------------------
# Payment operations
# ---------------------------------------------------------------------------


async def list_payments(
    db,
    org_id: str,
    contract_id: str,
    page: int = 1,
    per_page: int = 20,
) -> dict:
    """List payments for a contract with pagination.

    Raises:
        NotFoundError: If the contract does not exist.
    """
    contract = await crud.get_contract_by_id(db, contract_id)
    if contract is None or contract.organization_id != org_id:
        raise NotFoundError(message="Contract not found")

    items, total = await crud.list_payments_by_contract(
        db, org_id, contract_id, page, per_page
    )
    total_pages = (total + per_page - 1) // per_page if per_page > 0 else 0
    return {
        "items": [PaymentResponse.model_validate(p) for p in items],
        "page": page,
        "per_page": per_page,
        "total": total,
        "total_pages": total_pages,
    }


async def create_payment(
    db,
    org_id: str,
    contract_id: str,
    data: PaymentCreate,
    created_by: str | None = None,
) -> PaymentResponse:
    """Create a new payment for a contract with auto-incremented payment_no.

    Raises:
        NotFoundError: If the contract does not exist.
    """
    contract = await crud.get_contract_by_id(db, contract_id)
    if contract is None or contract.organization_id != org_id:
        raise NotFoundError(message="Contract not found")

    payment_no = await crud.count_payments_by_contract(db, contract_id) + 1

    payment = await crud.create_payment(
        db,
        organization_id=org_id,
        contract_id=contract_id,
        payment_no=payment_no,
        amount=data.amount,
        currency_code=data.currency_code,
        payment_date=data.payment_date,
        due_date=data.due_date,
        status=data.status,
        payment_method=data.payment_method,
        reference_number=data.reference_number,
        notes=data.notes,
        created_by=created_by,
    )
    await db.refresh(payment)
    return PaymentResponse.model_validate(payment)


async def update_payment(
    db,
    org_id: str,
    payment_id: str,
    data: PaymentUpdate,
) -> PaymentResponse:
    """Update an existing payment.

    Raises:
        NotFoundError: If the payment does not exist.
    """
    payment = await crud.get_payment_by_id(db, payment_id)
    if payment is None or payment.organization_id != org_id:
        raise NotFoundError(message="Payment not found")

    update_data = data.model_dump(exclude_unset=True)
    updated = await crud.update_payment(db, payment_id, **update_data)
    await db.refresh(updated)
    return PaymentResponse.model_validate(updated)
