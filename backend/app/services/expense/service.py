"""Expense service layer — business logic and validation.

Validates project references at the service layer, auto-generates
expense codes, handles approval workflow, and returns Pydantic schemas.
"""

from sqlalchemy import select

from app.core.exceptions import NotFoundError, ValidationError
from app.models.project import Project
from app.schemas.expense import (
    ExpenseApproveRequest,
    ExpenseCategory,
    ExpenseCreate,
    ExpenseResponse,
    ExpenseUpdate,
)
from app.services.expense import crud


async def get_expense(db, org_id: str, expense_id: str) -> ExpenseResponse:
    """Get a single expense by ID scoped to an organization.

    Args:
        db: Async database session.
        org_id: UUID string of the organization.
        expense_id: UUID string of the expense.

    Returns:
        ExpenseResponse schema.

    Raises:
        NotFoundError: If the expense does not exist or belongs to another org.
    """
    expense = await crud.get_expense_by_id(db, expense_id, org_id)
    if expense is None:
        raise NotFoundError(message="Expense not found")
    return ExpenseResponse.model_validate(expense)


async def list_expenses(
    db,
    org_id: str,
    page: int = 1,
    per_page: int = 20,
    project_id: str | None = None,
    category: str | None = None,
    approval_status: str | None = None,
) -> dict:
    """List expenses in an organization with pagination and optional filters.

    Args:
        db: Async database session.
        org_id: UUID string of the organization.
        page: 1-based page index.
        per_page: Items per page.
        project_id: Optional project filter.
        category: Optional category filter.
        approval_status: Optional approval status filter.

    Returns:
        Dict with items list and pagination metadata.
    """
    items, total = await crud.list_expenses_by_org(
        db, org_id, page, per_page,
        project_id=project_id,
        category=category,
        approval_status=approval_status,
    )
    total_pages = (total + per_page - 1) // per_page if per_page > 0 else 0
    return {
        "items": [ExpenseResponse.model_validate(e) for e in items],
        "page": page,
        "per_page": per_page,
        "total": total,
        "total_pages": total_pages,
    }


async def create_expense(
    db, org_id: str, data: ExpenseCreate, recorded_by: str | None = None
) -> ExpenseResponse:
    """Create a new expense with auto-generated code and project validation.

    Args:
        db: Async database session.
        org_id: UUID string of the organization.
        data: Validated ExpenseCreate payload.
        recorded_by: UUID string of the user recording the expense.

    Returns:
        ExpenseResponse schema for the newly created expense.

    Raises:
        NotFoundError: If the referenced project does not exist.
        ValidationError: If category is invalid.
    """
    # Validate project_id exists
    stmt = select(Project).where(
        Project.id == data.project_id,
        Project.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    project = result.scalar_one_or_none()
    if project is None:
        raise NotFoundError(
            message="Referenced project not found",
            details={"project_id": data.project_id},
        )

    # Validate category against enum if provided
    if data.category is not None:
        valid_categories = [c.value for c in ExpenseCategory]
        if data.category not in valid_categories:
            raise ValidationError(
                message=f"Invalid category. Must be one of: {valid_categories}",
                details={"category": data.category},
            )

    # Auto-generate expense code: EXP-{count+1}
    count = await crud.count_expenses_by_org(db, org_id)
    code = f"EXP-{count + 1}"

    expense = await crud.create_expense(
        db,
        organization_id=org_id,
        project_id=data.project_id,
        expense_code=code,
        category=data.category,
        description=data.description,
        amount=data.amount,
        currency_code=data.currency_code,
        expense_date=data.expense_date,
        recorded_by=recorded_by or data.recorded_by,
        payment_method=data.payment_method,
        receipt_url=data.receipt_url,
        notes=data.notes,
    )
    return ExpenseResponse.model_validate(expense)


async def update_expense(
    db, org_id: str, expense_id: str, data: ExpenseUpdate
) -> ExpenseResponse:
    """Update an existing expense.

    Args:
        db: Async database session.
        org_id: UUID string of the organization.
        expense_id: UUID string of the expense.
        data: Validated ExpenseUpdate payload.

    Returns:
        ExpenseResponse schema.

    Raises:
        NotFoundError: If the expense does not exist or belongs to another org.
        ValidationError: If category is invalid.
    """
    expense = await crud.get_expense_by_id(db, expense_id, org_id)
    if expense is None:
        raise NotFoundError(message="Expense not found")

    # Validate category against enum if being changed
    if data.category is not None:
        valid_categories = [c.value for c in ExpenseCategory]
        if data.category not in valid_categories:
            raise ValidationError(
                message=f"Invalid category. Must be one of: {valid_categories}",
                details={"category": data.category},
            )

    update_data = data.model_dump(exclude_unset=True)
    updated = await crud.update_expense(db, expense_id, **update_data)
    return ExpenseResponse.model_validate(updated)


async def approve_expense(
    db, org_id: str, expense_id: str, data: ExpenseApproveRequest, approved_by: str
) -> ExpenseResponse:
    """Approve or reject an expense.

    Args:
        db: Async database session.
        org_id: UUID string of the organization.
        expense_id: UUID string of the expense.
        data: Validated ExpenseApproveRequest payload.
        approved_by: UUID string of the user approving/rejecting.

    Returns:
        ExpenseResponse schema.

    Raises:
        NotFoundError: If the expense does not exist or belongs to another org.
        ValidationError: If the expense is already approved/rejected.
    """
    expense = await crud.get_expense_by_id(db, expense_id, org_id)
    if expense is None:
        raise NotFoundError(message="Expense not found")

    if expense.approval_status not in ("pending",):
        raise ValidationError(
            message=f"Cannot change status — expense is already '{expense.approval_status}'",
            details={"approval_status": expense.approval_status},
        )

    update_notes = data.notes
    updated = await crud.update_expense(
        db,
        expense_id,
        approval_status=data.status,
        approved_by=approved_by,
        notes=update_notes if update_notes is not None else expense.notes,
    )
    return ExpenseResponse.model_validate(updated)


async def delete_expense(db, org_id: str, expense_id: str) -> None:
    """Soft-delete an expense.

    Args:
        db: Async database session.
        org_id: UUID string of the organization.
        expense_id: UUID string of the expense.

    Raises:
        NotFoundError: If the expense does not exist or belongs to another org.
    """
    expense = await crud.get_expense_by_id(db, expense_id, org_id)
    if expense is None:
        raise NotFoundError(message="Expense not found")

    await crud.delete_expense(db, expense_id)
