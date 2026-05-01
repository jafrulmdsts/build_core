"""Employee service layer — business logic and validation.

Generates employee codes, validates inputs, and returns
Pydantic response schemas.
"""

from app.core.exceptions import NotFoundError
from app.schemas.employee import EmployeeCreate, EmployeeResponse, EmployeeUpdate
from app.services.employee import crud


async def get_employee(db, org_id: str, emp_id: str) -> EmployeeResponse:
    """Get a single employee by ID.

    Args:
        db: Async database session.
        org_id: UUID string of the organization (for scoping).
        emp_id: UUID string of the employee.

    Returns:
        EmployeeResponse schema.

    Raises:
        NotFoundError: If the employee does not exist.
    """
    emp = await crud.get_employee_by_id(db, emp_id)
    if emp is None or emp.organization_id != org_id:
        raise NotFoundError(message="Employee not found")
    return EmployeeResponse.model_validate(emp)


async def list_employees(
    db,
    org_id: str,
    page: int = 1,
    per_page: int = 20,
) -> dict:
    """List employees for an organization with pagination.

    Args:
        db: Async database session.
        org_id: UUID string of the organization.
        page: 1-based page index.
        per_page: Items per page.

    Returns:
        Dict with items, pagination metadata.
    """
    items, total = await crud.list_employees_by_org(db, org_id, page, per_page)
    total_pages = (total + per_page - 1) // per_page if per_page > 0 else 0
    return {
        "items": [EmployeeResponse.model_validate(e) for e in items],
        "page": page,
        "per_page": per_page,
        "total": total,
        "total_pages": total_pages,
    }


async def create_employee(
    db,
    org_id: str,
    data: EmployeeCreate,
    created_by: str | None = None,
) -> EmployeeResponse:
    """Create a new employee with auto-generated employee code.

    Args:
        db: Async database session.
        org_id: UUID string of the organization.
        data: Validated EmployeeCreate payload.
        created_by: UUID of the user creating the employee.

    Returns:
        EmployeeResponse schema for the newly created employee.
    """
    count = await crud.count_employees_by_org(db, org_id)
    employee_code = f"EMP-{count + 1}"

    emp = await crud.create_employee(
        db,
        organization_id=org_id,
        employee_code=employee_code,
        first_name=data.first_name,
        last_name=data.last_name,
        phone=data.phone,
        email=data.email,
        designation=data.designation,
        employee_type=data.employee_type,
        department=data.department,
        salary=data.salary,
        currency_code=data.currency_code,
        joining_date=data.joining_date,
        nid_number=data.nid_number,
        address=data.address,
        emergency_contact=data.emergency_contact,
        bank_account=data.bank_account,
        created_by=created_by,
    )
    return EmployeeResponse.model_validate(emp)


async def update_employee(
    db,
    org_id: str,
    emp_id: str,
    data: EmployeeUpdate,
) -> EmployeeResponse:
    """Update an existing employee.

    Args:
        db: Async database session.
        org_id: UUID string of the organization (for scoping).
        emp_id: UUID string of the employee.
        data: Validated EmployeeUpdate payload.

    Returns:
        EmployeeResponse schema.

    Raises:
        NotFoundError: If the employee does not exist.
    """
    emp = await crud.get_employee_by_id(db, emp_id)
    if emp is None or emp.organization_id != org_id:
        raise NotFoundError(message="Employee not found")

    update_data = data.model_dump(exclude_unset=True)
    updated = await crud.update_employee(db, emp_id, **update_data)
    return EmployeeResponse.model_validate(updated)


async def delete_employee(db, org_id: str, emp_id: str) -> None:
    """Soft-delete an employee.

    Args:
        db: Async database session.
        org_id: UUID string of the organization (for scoping).
        emp_id: UUID string of the employee.

    Raises:
        NotFoundError: If the employee does not exist.
    """
    emp = await crud.get_employee_by_id(db, emp_id)
    if emp is None or emp.organization_id != org_id:
        raise NotFoundError(message="Employee not found")

    deleted = await crud.delete_employee(db, emp_id)
    if not deleted:
        raise NotFoundError(message="Employee not found")
