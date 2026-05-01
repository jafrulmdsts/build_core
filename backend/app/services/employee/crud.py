"""Employee CRUD operations — low-level database access.

All queries filter out soft-deleted records (deleted_at IS NULL).
"""

from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.employee import Employee


async def get_employee_by_id(db: AsyncSession, emp_id: str) -> Employee | None:
    """Fetch a single employee by ID (excludes soft-deleted).

    Args:
        db: Async database session.
        emp_id: UUID string of the employee.

    Returns:
        Employee row or None if not found / deleted.
    """
    stmt = select(Employee).where(
        Employee.id == emp_id,
        Employee.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def list_employees_by_org(
    db: AsyncSession,
    org_id: str,
    page: int = 1,
    per_page: int = 20,
) -> tuple[list[Employee], int]:
    """List employees for an organization with pagination (excludes soft-deleted).

    Args:
        db: Async database session.
        org_id: UUID string of the organization.
        page: 1-based page index.
        per_page: Items per page.

    Returns:
        Tuple of (items, total_count).
    """
    base_filter = (
        Employee.organization_id == org_id,
        Employee.deleted_at.is_(None),
    )

    # Count
    count_stmt = select(func.count()).select_from(Employee).where(*base_filter)
    total = (await db.execute(count_stmt)).scalar_one()

    # Fetch page
    offset = (page - 1) * per_page
    stmt = (
        select(Employee)
        .where(*base_filter)
        .order_by(Employee.created_at.desc())
        .offset(offset)
        .limit(per_page)
    )
    result = await db.execute(stmt)
    items = list(result.scalars().all())

    return items, total


async def count_employees_by_org(db: AsyncSession, org_id: str) -> int:
    """Count active (non-deleted) employees for an organization.

    Used for employee_code generation.

    Args:
        db: Async database session.
        org_id: UUID string of the organization.

    Returns:
        Number of active employees.
    """
    stmt = select(func.count()).select_from(Employee).where(
        Employee.organization_id == org_id,
        Employee.deleted_at.is_(None),
    )
    return (await db.execute(stmt)).scalar_one()


async def create_employee(db: AsyncSession, **kwargs: object) -> Employee:
    """Create a new employee and flush to the session.

    Args:
        db: Async database session.
        **kwargs: Column values for the new Employee.

    Returns:
        The new Employee instance (id populated after flush).
    """
    emp = Employee(**kwargs)
    db.add(emp)
    await db.flush()
    return emp


async def update_employee(
    db: AsyncSession,
    emp_id: str,
    **kwargs: object,
) -> Employee | None:
    """Update an employee by ID (excludes soft-deleted).

    Args:
        db: Async database session.
        emp_id: UUID string of the employee.
        **kwargs: Column values to update.

    Returns:
        Updated Employee row or None if not found.
    """
    stmt = select(Employee).where(
        Employee.id == emp_id,
        Employee.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    emp = result.scalar_one_or_none()
    if emp is None:
        return None

    for key, value in kwargs.items():
        if value is not None:
            setattr(emp, key, value)

    await db.flush()
    return emp


async def delete_employee(db: AsyncSession, emp_id: str) -> bool:
    """Soft-delete an employee by setting deleted_at.

    Args:
        db: Async database session.
        emp_id: UUID string of the employee.

    Returns:
        True if the employee was found and soft-deleted, False otherwise.
    """
    stmt = select(Employee).where(
        Employee.id == emp_id,
        Employee.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    emp = result.scalar_one_or_none()
    if emp is None:
        return False

    emp.deleted_at = datetime.now(timezone.utc)
    await db.flush()
    return True
