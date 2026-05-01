"""Contractor CRUD operations — low-level database access.

All queries filter out soft-deleted records (deleted_at IS NULL).
"""

from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.contractor import Contractor, ContractorContract, ContractorPayment


# ---------------------------------------------------------------------------
# Contractor CRUD
# ---------------------------------------------------------------------------


async def get_contractor_by_id(db: AsyncSession, ctr_id: str) -> Contractor | None:
    """Fetch a single contractor by ID (excludes soft-deleted)."""
    stmt = select(Contractor).where(
        Contractor.id == ctr_id,
        Contractor.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def list_contractors_by_org(
    db: AsyncSession,
    org_id: str,
    page: int = 1,
    per_page: int = 20,
) -> tuple[list[Contractor], int]:
    """List contractors for an organization with pagination."""
    base_filter = (
        Contractor.organization_id == org_id,
        Contractor.deleted_at.is_(None),
    )

    count_stmt = select(func.count()).select_from(Contractor).where(*base_filter)
    total = (await db.execute(count_stmt)).scalar_one()

    offset = (page - 1) * per_page
    stmt = (
        select(Contractor)
        .where(*base_filter)
        .order_by(Contractor.created_at.desc())
        .offset(offset)
        .limit(per_page)
    )
    result = await db.execute(stmt)
    items = list(result.scalars().all())
    return items, total


async def count_contractors_by_org(db: AsyncSession, org_id: str) -> int:
    """Count active contractors for code generation."""
    stmt = select(func.count()).select_from(Contractor).where(
        Contractor.organization_id == org_id,
        Contractor.deleted_at.is_(None),
    )
    return (await db.execute(stmt)).scalar_one()


async def create_contractor(db: AsyncSession, **kwargs: object) -> Contractor:
    """Create a new contractor and flush."""
    ctr = Contractor(**kwargs)
    db.add(ctr)
    await db.flush()
    return ctr


async def update_contractor(
    db: AsyncSession,
    ctr_id: str,
    **kwargs: object,
) -> Contractor | None:
    """Update a contractor by ID (excludes soft-deleted)."""
    stmt = select(Contractor).where(
        Contractor.id == ctr_id,
        Contractor.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    ctr = result.scalar_one_or_none()
    if ctr is None:
        return None

    for key, value in kwargs.items():
        if value is not None:
            setattr(ctr, key, value)

    await db.flush()
    return ctr


async def delete_contractor(db: AsyncSession, ctr_id: str) -> bool:
    """Soft-delete a contractor."""
    stmt = select(Contractor).where(
        Contractor.id == ctr_id,
        Contractor.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    ctr = result.scalar_one_or_none()
    if ctr is None:
        return False

    ctr.deleted_at = datetime.now(timezone.utc)
    await db.flush()
    return True


# ---------------------------------------------------------------------------
# ContractorContract CRUD
# ---------------------------------------------------------------------------


async def get_contract_by_id(db: AsyncSession, contract_id: str) -> ContractorContract | None:
    """Fetch a single contract by ID (excludes soft-deleted)."""
    stmt = select(ContractorContract).where(
        ContractorContract.id == contract_id,
        ContractorContract.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def list_contracts_by_contractor(
    db: AsyncSession,
    org_id: str,
    contractor_id: str,
    page: int = 1,
    per_page: int = 20,
) -> tuple[list[ContractorContract], int]:
    """List contracts for a specific contractor."""
    base_filter = (
        ContractorContract.organization_id == org_id,
        ContractorContract.contractor_id == contractor_id,
        ContractorContract.deleted_at.is_(None),
    )

    count_stmt = select(func.count()).select_from(ContractorContract).where(*base_filter)
    total = (await db.execute(count_stmt)).scalar_one()

    offset = (page - 1) * per_page
    stmt = (
        select(ContractorContract)
        .where(*base_filter)
        .order_by(ContractorContract.created_at.desc())
        .offset(offset)
        .limit(per_page)
    )
    result = await db.execute(stmt)
    items = list(result.scalars().all())
    return items, total


async def list_contracts_by_project(
    db: AsyncSession,
    org_id: str,
    project_id: str,
) -> list[ContractorContract]:
    """List all contracts for a specific project."""
    stmt = select(ContractorContract).where(
        ContractorContract.organization_id == org_id,
        ContractorContract.project_id == project_id,
        ContractorContract.deleted_at.is_(None),
    ).order_by(ContractorContract.created_at.desc())
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def count_contracts_by_org(db: AsyncSession, org_id: str) -> int:
    """Count active contracts for code generation."""
    stmt = select(func.count()).select_from(ContractorContract).where(
        ContractorContract.organization_id == org_id,
        ContractorContract.deleted_at.is_(None),
    )
    return (await db.execute(stmt)).scalar_one()


async def create_contract(db: AsyncSession, **kwargs: object) -> ContractorContract:
    """Create a new contract and flush."""
    contract = ContractorContract(**kwargs)
    db.add(contract)
    await db.flush()
    return contract


async def update_contract(
    db: AsyncSession,
    contract_id: str,
    **kwargs: object,
) -> ContractorContract | None:
    """Update a contract by ID (excludes soft-deleted)."""
    stmt = select(ContractorContract).where(
        ContractorContract.id == contract_id,
        ContractorContract.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    contract = result.scalar_one_or_none()
    if contract is None:
        return None

    for key, value in kwargs.items():
        if value is not None:
            setattr(contract, key, value)

    await db.flush()
    return contract


# ---------------------------------------------------------------------------
# ContractorPayment CRUD
# ---------------------------------------------------------------------------


async def get_payment_by_id(db: AsyncSession, payment_id: str) -> ContractorPayment | None:
    """Fetch a single payment by ID (excludes soft-deleted)."""
    stmt = select(ContractorPayment).where(
        ContractorPayment.id == payment_id,
        ContractorPayment.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def list_payments_by_contract(
    db: AsyncSession,
    org_id: str,
    contract_id: str,
    page: int = 1,
    per_page: int = 20,
) -> tuple[list[ContractorPayment], int]:
    """List payments for a specific contract."""
    base_filter = (
        ContractorPayment.organization_id == org_id,
        ContractorPayment.contract_id == contract_id,
        ContractorPayment.deleted_at.is_(None),
    )

    count_stmt = select(func.count()).select_from(ContractorPayment).where(*base_filter)
    total = (await db.execute(count_stmt)).scalar_one()

    offset = (page - 1) * per_page
    stmt = (
        select(ContractorPayment)
        .where(*base_filter)
        .order_by(ContractorPayment.created_at.desc())
        .offset(offset)
        .limit(per_page)
    )
    result = await db.execute(stmt)
    items = list(result.scalars().all())
    return items, total


async def count_payments_by_contract(
    db: AsyncSession,
    contract_id: str,
) -> int:
    """Count active payments for a contract (for payment_no generation)."""
    stmt = select(func.count()).select_from(ContractorPayment).where(
        ContractorPayment.contract_id == contract_id,
        ContractorPayment.deleted_at.is_(None),
    )
    return (await db.execute(stmt)).scalar_one()


async def create_payment(db: AsyncSession, **kwargs: object) -> ContractorPayment:
    """Create a new payment and flush."""
    payment = ContractorPayment(**kwargs)
    db.add(payment)
    await db.flush()
    return payment


async def update_payment(
    db: AsyncSession,
    payment_id: str,
    **kwargs: object,
) -> ContractorPayment | None:
    """Update a payment by ID (excludes soft-deleted)."""
    stmt = select(ContractorPayment).where(
        ContractorPayment.id == payment_id,
        ContractorPayment.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    payment = result.scalar_one_or_none()
    if payment is None:
        return None

    for key, value in kwargs.items():
        if value is not None:
            setattr(payment, key, value)

    await db.flush()
    return payment
