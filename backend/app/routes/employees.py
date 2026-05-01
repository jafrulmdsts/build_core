"""
BuildCore Employee Routes.

CRUD endpoints for managing employees. Tenant context required for
all operations; super admin required for delete.
"""

from fastapi import APIRouter, Depends

from app.core.exceptions import BuildCoreError
from app.core.pagination import get_pagination_params
from app.core.responses import error_response, paginated_response, success_response
from app.core.dependencies import require_tenant, require_super_admin, get_db_session
from app.schemas.employee import EmployeeCreate, EmployeeUpdate
from app.services.employee.service import (
    get_employee as svc_get_employee,
    list_employees as svc_list_employees,
    create_employee as svc_create_employee,
    update_employee as svc_update_employee,
    delete_employee as svc_delete_employee,
)

router = APIRouter(prefix="/employees", tags=["Employees"])


@router.get("/")
async def list_employees_endpoint(
    db=Depends(get_db_session),
    pagination=Depends(get_pagination_params),
    current_user: dict = Depends(require_tenant),
):
    """List all employees for the tenant organization. Supports pagination."""
    try:
        org_id = current_user.get("organization_id")
        result = await svc_list_employees(
            db, org_id=org_id, page=pagination.page, per_page=pagination.per_page
        )
        return paginated_response(
            data=result["items"],
            page=result["page"],
            per_page=result["per_page"],
            total=result["total"],
            message="Employees retrieved",
        )
    except BuildCoreError as exc:
        return error_response(exc)


@router.post("/")
async def create_employee_endpoint(
    body: EmployeeCreate,
    db=Depends(get_db_session),
    current_user: dict = Depends(require_tenant),
):
    """Create a new employee. Requires tenant context."""
    try:
        org_id = current_user.get("organization_id")
        user_id = current_user.get("sub")
        emp = await svc_create_employee(db, org_id=org_id, data=body, created_by=user_id)
        return success_response(data=emp, message="Employee created", meta={"status_code": 201})
    except BuildCoreError as exc:
        return error_response(exc)


@router.get("/{emp_id}")
async def get_employee_endpoint(
    emp_id: str,
    db=Depends(get_db_session),
    current_user: dict = Depends(require_tenant),
):
    """Retrieve a single employee by ID. Requires tenant context."""
    try:
        org_id = current_user.get("organization_id")
        emp = await svc_get_employee(db, org_id=org_id, emp_id=emp_id)
        return success_response(data=emp, message="Employee retrieved")
    except BuildCoreError as exc:
        return error_response(exc)


@router.put("/{emp_id}")
async def update_employee_endpoint(
    emp_id: str,
    body: EmployeeUpdate,
    db=Depends(get_db_session),
    current_user: dict = Depends(require_tenant),
):
    """Update an existing employee. Requires tenant context."""
    try:
        org_id = current_user.get("organization_id")
        emp = await svc_update_employee(db, org_id=org_id, emp_id=emp_id, data=body)
        return success_response(data=emp, message="Employee updated")
    except BuildCoreError as exc:
        return error_response(exc)


@router.delete("/{emp_id}")
async def delete_employee_endpoint(
    emp_id: str,
    db=Depends(get_db_session),
    _current_user: dict = Depends(require_super_admin),
):
    """Soft-delete an employee. Super admin only."""
    try:
        # Super admin can delete any employee; we need org_id from path context
        # For safety, retrieve the employee first to get org_id
        from app.services.employee import crud
        emp = await crud.get_employee_by_id(db, emp_id)
        if emp is None:
            from app.core.exceptions import NotFoundError
            raise NotFoundError(message="Employee not found")
        await svc_delete_employee(db, org_id=emp.organization_id, emp_id=emp_id)
        return success_response(message="Employee deleted")
    except BuildCoreError as exc:
        return error_response(exc)
