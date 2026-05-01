"""Project CRUD operations — low-level database access.

All queries filter out soft-deleted records (deleted_at IS NULL)
and scope results to the given organization_id.
"""

from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project


async def get_project_by_id(
    db: AsyncSession, project_id: str, org_id: str
) -> Project | None:
    """Fetch a single project by ID scoped to an organization.

    Args:
        db: Async database session.
        project_id: UUID string of the project.
        org_id: UUID string of the organization.

    Returns:
        Project row or None if not found / deleted / wrong org.
    """
    stmt = select(Project).where(
        Project.id == project_id,
        Project.organization_id == org_id,
        Project.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def list_projects_by_org(
    db: AsyncSession,
    org_id: str,
    page: int = 1,
    per_page: int = 20,
    status: str | None = None,
    project_type: str | None = None,
) -> tuple[list[Project], int]:
    """List projects belonging to an organization with pagination.

    Args:
        db: Async database session.
        org_id: UUID string of the organization.
        page: 1-based page index.
        per_page: Items per page.
        status: Optional status filter.
        project_type: Optional project_type filter.

    Returns:
        Tuple of (items, total_count).
    """
    filters = [
        Project.organization_id == org_id,
        Project.deleted_at.is_(None),
    ]

    if status is not None:
        filters.append(Project.status == status)
    if project_type is not None:
        filters.append(Project.project_type == project_type)

    # Count
    count_stmt = select(func.count()).select_from(Project).where(*filters)
    total = (await db.execute(count_stmt)).scalar_one()

    # Fetch page
    offset = (page - 1) * per_page
    stmt = (
        select(Project)
        .where(*filters)
        .order_by(Project.created_at.desc())
        .offset(offset)
        .limit(per_page)
    )
    result = await db.execute(stmt)
    items = list(result.scalars().all())

    return items, total


async def count_projects_by_org(db: AsyncSession, org_id: str) -> int:
    """Count active (non-deleted) projects for an organization.

    Used for auto-generating the project code (PRJ-{count+1}).

    Args:
        db: Async database session.
        org_id: UUID string of the organization.

    Returns:
        Number of active projects in the organization.
    """
    stmt = select(func.count()).select_from(Project).where(
        Project.organization_id == org_id,
        Project.deleted_at.is_(None),
    )
    return (await db.execute(stmt)).scalar_one()


async def create_project(db: AsyncSession, **kwargs: object) -> Project:
    """Create a new project and flush to the session.

    Args:
        db: Async database session.
        **kwargs: Column values for the new Project.

    Returns:
        The new Project instance (id populated after flush).
    """
    project = Project(**kwargs)
    db.add(project)
    await db.flush()
    return project


async def update_project(
    db: AsyncSession, project_id: str, **kwargs: object
) -> Project | None:
    """Update a project by ID (excludes soft-deleted).

    Args:
        db: Async database session.
        project_id: UUID string of the project.
        **kwargs: Column values to update.

    Returns:
        Updated Project row or None if not found.
    """
    stmt = select(Project).where(
        Project.id == project_id,
        Project.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    project = result.scalar_one_or_none()
    if project is None:
        return None

    for key, value in kwargs.items():
        if value is not None:
            setattr(project, key, value)

    await db.flush()
    return project


async def delete_project(db: AsyncSession, project_id: str) -> bool:
    """Soft-delete a project by setting deleted_at.

    Args:
        db: Async database session.
        project_id: UUID string of the project.

    Returns:
        True if the project was found and soft-deleted, False otherwise.
    """
    stmt = select(Project).where(
        Project.id == project_id,
        Project.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    project = result.scalar_one_or_none()
    if project is None:
        return False

    project.deleted_at = datetime.now(timezone.utc)
    await db.flush()
    return True
