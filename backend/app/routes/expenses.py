"""
BuildCore Expense Routes.

CRUD endpoints for managing project expenses. Tenant context required
for all operations; super admin required for delete. Includes approval
workflow via PATCH approve endpoint.
"""

from fastapi import APIRouter, Depends, Query

from app.core.dependencies import require_super_admin, require_tenant, get_db_session
from app.core.exceptions import BuildCoreError
from app.core.pagination import get_pagination_params
from app.core.responses import error_response, paginated_response, success_response
from app.schemas.expense import ExpenseApproveRequest, ExpenseCreate, ExpenseUpdate
from app.services.expense.service import (
    approve_expense as approve_expense_svc,
    create_expense as create_expense_svc,
    delete_expense as delete_expense_svc,
    get_expense as get_expense_svc,
    list_expenses as list_expenses_svc,
    update_expense as update_expense_svc,
)

router = APIRouter(prefix="/expenses", tags=["Expenses"])


@router.get("/")
async def list_expenses_endpoint(
    db=Depends(get_db_session),
    pagination=Depends(get_pagination_params),
    current_user: dict = Depends(require_tenant),
    project_id: str | None = Query(default=None, description="Filter by project ID"),
    category: str | None = Query(default=None, description="Filter by category"),
    approval_status: str | None = Query(default=None, description="Filter by approval status"),
):
    """List expenses within the authenticated organization. Supports pagination and filters."""
    try:
        organization_id = current_user.get("organization_id")
        result = await list_expenses_svc(
            db,
            org_id=organization_id,
            page=pagination.page,
            per_page=pagination.per_page,
            project_id=project_id,
            category=category,
            approval_status=approval_status,
        )
        return paginated_response(
            data=result["items"],
            page=result["page"],
            per_page=result["per_page"],
            total=result["total"],
            message="Expenses retrieved",
        )
    except BuildCoreError as exc:
        return error_response(exc)


@router.post("/")
async def create_expense_endpoint(
    body: ExpenseCreate,
    db=Depends(get_db_session),
    current_user: dict = Depends(require_tenant),
):
    """Create a new expense within the authenticated organization."""
    try:
        organization_id = current_user.get("organization_id")
        recorded_by = current_user.get("sub")
        expense = await create_expense_svc(
            db, org_id=organization_id, data=body, recorded_by=recorded_by
        )
        return success_response(data=expense, message="Expense created")
    except BuildCoreError as exc:
        return error_response(exc)


@router.get("/{expense_id}")
async def get_expense_endpoint(
    expense_id: str,
    db=Depends(get_db_session),
    current_user: dict = Depends(require_tenant),
):
    """Retrieve a single expense by ID. Requires tenant context."""
    try:
        organization_id = current_user.get("organization_id")
        expense = await get_expense_svc(
            db, org_id=organization_id, expense_id=expense_id
        )
        return success_response(data=expense, message="Expense retrieved")
    except BuildCoreError as exc:
        return error_response(exc)


@router.put("/{expense_id}")
async def update_expense_endpoint(
    expense_id: str,
    body: ExpenseUpdate,
    db=Depends(get_db_session),
    current_user: dict = Depends(require_tenant),
):
    """Update an existing expense. Requires tenant context."""
    try:
        organization_id = current_user.get("organization_id")
        expense = await update_expense_svc(
            db, org_id=organization_id, expense_id=expense_id, data=body
        )
        return success_response(data=expense, message="Expense updated")
    except BuildCoreError as exc:
        return error_response(exc)


@router.patch("/{expense_id}/approve")
async def approve_expense_endpoint(
    expense_id: str,
    body: ExpenseApproveRequest,
    db=Depends(get_db_session),
    current_user: dict = Depends(require_tenant),
):
    """Approve or reject an expense. Requires tenant context."""
    try:
        organization_id = current_user.get("organization_id")
        approved_by = current_user.get("sub")
        expense = await approve_expense_svc(
            db,
            org_id=organization_id,
            expense_id=expense_id,
            data=body,
            approved_by=approved_by,
        )
        return success_response(data=expense, message="Expense approval updated")
    except BuildCoreError as exc:
        return error_response(exc)


@router.delete("/{expense_id}")
async def delete_expense_endpoint(
    expense_id: str,
    db=Depends(get_db_session),
    _current_user: dict = Depends(require_super_admin),
):
    """Soft-delete an expense (super admin only)."""
    try:
        from app.services.expense import crud
        expense = await crud.get_expense_by_id(db, expense_id, _current_user.get("organization_id"))
        if expense is None:
            from app.core.exceptions import NotFoundError
            raise NotFoundError(message="Expense not found")
        await delete_expense_svc(
            db, org_id=expense.organization_id, expense_id=expense_id
        )
        return success_response(message="Expense deleted")
    except BuildCoreError as exc:
        return error_response(exc)
