"""Expense CRUD operations — low-level database access.

All queries filter out soft-deleted records (deleted_at IS NULL)
and scope results to the given organization_id.
"""

from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.expense import ProjectExpense


async def get_expense_by_id(
    db: AsyncSession, expense_id: str, org_id: str
) -> ProjectExpense | None:
    """Fetch a single expense by ID scoped to an organization.

    Args:
        db: Async database session.
        expense_id: UUID string of the expense.
        org_id: UUID string of the organization.

    Returns:
        ProjectExpense row or None if not found / deleted / wrong org.
    """
    stmt = select(ProjectExpense).where(
        ProjectExpense.id == expense_id,
        ProjectExpense.organization_id == org_id,
        ProjectExpense.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def list_expenses_by_org(
    db: AsyncSession,
    org_id: str,
    page: int = 1,
    per_page: int = 20,
    project_id: str | None = None,
    category: str | None = None,
    approval_status: str | None = None,
) -> tuple[list[ProjectExpense], int]:
    """List expenses for an organization with pagination and filters.

    Args:
        db: Async database session.
        org_id: UUID string of the organization.
        page: 1-based page index.
        per_page: Items per page.
        project_id: Optional project filter.
        category: Optional category filter.
        approval_status: Optional approval status filter.

    Returns:
        Tuple of (items, total_count).
    """
    filters = [
        ProjectExpense.organization_id == org_id,
        ProjectExpense.deleted_at.is_(None),
    ]

    if project_id is not None:
        filters.append(ProjectExpense.project_id == project_id)
    if category is not None:
        filters.append(ProjectExpense.category == category)
    if approval_status is not None:
        filters.append(ProjectExpense.approval_status == approval_status)

    # Count
    count_stmt = select(func.count()).select_from(ProjectExpense).where(*filters)
    total = (await db.execute(count_stmt)).scalar_one()

    # Fetch page
    offset = (page - 1) * per_page
    stmt = (
        select(ProjectExpense)
        .where(*filters)
        .order_by(ProjectExpense.created_at.desc())
        .offset(offset)
        .limit(per_page)
    )
    result = await db.execute(stmt)
    items = list(result.scalars().all())

    return items, total


async def count_expenses_by_org(db: AsyncSession, org_id: str) -> int:
    """Count active (non-deleted) expenses for an organization.

    Used for auto-generating the expense code (EXP-{count+1}).

    Args:
        db: Async database session.
        org_id: UUID string of the organization.

    Returns:
        Number of active expenses in the organization.
    """
    stmt = select(func.count()).select_from(ProjectExpense).where(
        ProjectExpense.organization_id == org_id,
        ProjectExpense.deleted_at.is_(None),
    )
    return (await db.execute(stmt)).scalar_one()


async def create_expense(db: AsyncSession, **kwargs: object) -> ProjectExpense:
    """Create a new expense and flush to the session.

    Args:
        db: Async database session.
        **kwargs: Column values for the new ProjectExpense.

    Returns:
        The new ProjectExpense instance (id populated after flush).
    """
    expense = ProjectExpense(**kwargs)
    db.add(expense)
    await db.flush()
    return expense


async def update_expense(
    db: AsyncSession, expense_id: str, **kwargs: object
) -> ProjectExpense | None:
    """Update an expense by ID (excludes soft-deleted).

    Args:
        db: Async database session.
        expense_id: UUID string of the expense.
        **kwargs: Column values to update.

    Returns:
        Updated ProjectExpense row or None if not found.
    """
    stmt = select(ProjectExpense).where(
        ProjectExpense.id == expense_id,
        ProjectExpense.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    expense = result.scalar_one_or_none()
    if expense is None:
        return None

    for key, value in kwargs.items():
        if value is not None:
            setattr(expense, key, value)

    await db.flush()
    return expense


async def delete_expense(db: AsyncSession, expense_id: str) -> bool:
    """Soft-delete an expense by setting deleted_at.

    Args:
        db: Async database session.
        expense_id: UUID string of the expense.

    Returns:
        True if the expense was found and soft-deleted, False otherwise.
    """
    stmt = select(ProjectExpense).where(
        ProjectExpense.id == expense_id,
        ProjectExpense.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    expense = result.scalar_one_or_none()
    if expense is None:
        return False

    expense.deleted_at = datetime.now(timezone.utc)
    await db.flush()
    return True
