"""Project service layer — business logic and validation.

Validates cross-entity references (e.g. manager_id) at the service layer,
auto-generates project codes, and returns Pydantic response schemas.
"""

from sqlalchemy import select

from app.core.exceptions import NotFoundError, ValidationError
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from app.services.project import crud


async def get_project(db, org_id: str, project_id: str) -> ProjectResponse:
    """Get a single project by ID scoped to an organization.

    Args:
        db: Async database session.
        org_id: UUID string of the organization.
        project_id: UUID string of the project.

    Returns:
        ProjectResponse schema.

    Raises:
        NotFoundError: If the project does not exist or belongs to another org.
    """
    project = await crud.get_project_by_id(db, project_id, org_id)
    if project is None:
        raise NotFoundError(message="Project not found")
    return ProjectResponse.model_validate(project)


async def list_projects(
    db,
    org_id: str,
    page: int = 1,
    per_page: int = 20,
    status: str | None = None,
    project_type: str | None = None,
) -> dict:
    """List projects in an organization with pagination and optional filters.

    Args:
        db: Async database session.
        org_id: UUID string of the organization.
        page: 1-based page index.
        per_page: Items per page.
        status: Optional status filter.
        project_type: Optional project_type filter.

    Returns:
        Dict with items list and pagination metadata.
    """
    items, total = await crud.list_projects_by_org(
        db, org_id, page, per_page, status=status, project_type=project_type
    )
    total_pages = (total + per_page - 1) // per_page if per_page > 0 else 0
    return {
        "items": [ProjectResponse.model_validate(p) for p in items],
        "page": page,
        "per_page": per_page,
        "total": total,
        "total_pages": total_pages,
    }


async def create_project(
    db, org_id: str, data: ProjectCreate, created_by: str
) -> ProjectResponse:
    """Create a new project with auto-generated code and manager validation.

    Args:
        db: Async database session.
        org_id: UUID string of the organization.
        data: Validated ProjectCreate payload.
        created_by: UUID string of the user creating the project.

    Returns:
        ProjectResponse schema for the newly created project.

    Raises:
        ValidationError: If the provided manager_id is invalid.
    """
    # Validate manager_id if provided
    if data.manager_id is not None:
        stmt = select(User).where(
            User.id == data.manager_id,
            User.deleted_at.is_(None),
        )
        result = await db.execute(stmt)
        manager = result.scalar_one_or_none()
        if manager is None:
            raise ValidationError(
                message="Invalid manager — user not found",
                details={"manager_id": data.manager_id},
            )

    # Auto-generate project code: PRJ-{count+1}
    count = await crud.count_projects_by_org(db, org_id)
    code = f"PRJ-{count + 1}"

    project = await crud.create_project(
        db,
        organization_id=org_id,
        name=data.name,
        code=code,
        description=data.description,
        country_id=data.country_id,
        division_id=data.division_id,
        district_id=data.district_id,
        upazila_id=data.upazila_id,
        post_office_id=data.post_office_id,
        village=data.village,
        full_address=data.full_address,
        latitude=data.latitude,
        longitude=data.longitude,
        start_date=data.start_date,
        end_date=data.end_date,
        estimated_budget=data.estimated_budget,
        currency_code=data.currency_code,
        status=data.status,
        project_type=data.project_type,
        manager_id=data.manager_id,
        client_name=data.client_name,
        client_phone=data.client_phone,
        client_email=data.client_email,
        notes=data.notes,
        created_by=created_by,
    )
    return ProjectResponse.model_validate(project)


async def update_project(
    db, org_id: str, project_id: str, data: ProjectUpdate, updated_by: str
) -> ProjectResponse:
    """Update an existing project.

    Args:
        db: Async database session.
        org_id: UUID string of the organization.
        project_id: UUID string of the project.
        data: Validated ProjectUpdate payload.
        updated_by: UUID string of the user updating the project.

    Returns:
        ProjectResponse schema.

    Raises:
        NotFoundError: If the project does not exist or belongs to another org.
        ValidationError: If the provided manager_id is invalid.
    """
    project = await crud.get_project_by_id(db, project_id, org_id)
    if project is None:
        raise NotFoundError(message="Project not found")

    # Validate manager_id if being changed
    if data.manager_id is not None and data.manager_id != project.manager_id:
        stmt = select(User).where(
            User.id == data.manager_id,
            User.deleted_at.is_(None),
        )
        result = await db.execute(stmt)
        manager = result.scalar_one_or_none()
        if manager is None:
            raise ValidationError(
                message="Invalid manager — user not found",
                details={"manager_id": data.manager_id},
            )

    update_data = data.model_dump(exclude_unset=True)
    update_data["updated_by"] = updated_by
    updated = await crud.update_project(db, project_id, **update_data)
    return ProjectResponse.model_validate(updated)


async def delete_project(db, org_id: str, project_id: str) -> None:
    """Soft-delete a project.

    Args:
        db: Async database session.
        org_id: UUID string of the organization.
        project_id: UUID string of the project.

    Raises:
        NotFoundError: If the project does not exist or belongs to another org.
    """
    # Verify project belongs to the org before deleting
    project = await crud.get_project_by_id(db, project_id, org_id)
    if project is None:
        raise NotFoundError(message="Project not found")

    await crud.delete_project(db, project_id)
