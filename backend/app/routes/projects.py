"""
BuildCore Project Routes.

CRUD endpoints for managing construction projects.
Tenant-scoped for all operations; super admin required for delete.
"""

from fastapi import APIRouter, Depends, Query

from app.core.dependencies import require_super_admin, require_tenant, get_db_session
from app.core.exceptions import BuildCoreError
from app.core.pagination import get_pagination_params
from app.core.responses import error_response, paginated_response, success_response
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.services.project.service import (
    create_project as create_project_svc,
    delete_project as delete_project_svc,
    get_project as get_project_svc,
    list_projects as list_projects_svc,
    update_project as update_project_svc,
)

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.get("/")
async def list_projects_endpoint(
    db=Depends(get_db_session),
    pagination=Depends(get_pagination_params),
    current_user: dict = Depends(require_tenant),
    status: str | None = Query(default=None, description="Filter by status"),
    project_type: str | None = Query(default=None, description="Filter by project type"),
):
    """List projects within the authenticated organization. Supports pagination and filters."""
    try:
        organization_id = current_user.get("organization_id")
        result = await list_projects_svc(
            db,
            org_id=organization_id,
            page=pagination.page,
            per_page=pagination.per_page,
            status=status,
            project_type=project_type,
        )
        return paginated_response(
            data=result["items"],
            page=result["page"],
            per_page=result["per_page"],
            total=result["total"],
            message="Projects retrieved",
        )
    except BuildCoreError as exc:
        return error_response(exc)


@router.post("/")
async def create_project_endpoint(
    body: ProjectCreate,
    db=Depends(get_db_session),
    current_user: dict = Depends(require_tenant),
):
    """Create a new project within the authenticated organization."""
    try:
        organization_id = current_user.get("organization_id")
        created_by = current_user.get("sub")
        project = await create_project_svc(
            db, org_id=organization_id, data=body, created_by=created_by
        )
        return success_response(data=project, message="Project created")
    except BuildCoreError as exc:
        return error_response(exc)


@router.get("/{project_id}")
async def get_project_endpoint(
    project_id: str,
    db=Depends(get_db_session),
    current_user: dict = Depends(require_tenant),
):
    """Retrieve a single project by ID. Requires tenant context."""
    try:
        organization_id = current_user.get("organization_id")
        project = await get_project_svc(db, org_id=organization_id, project_id=project_id)
        return success_response(data=project, message="Project retrieved")
    except BuildCoreError as exc:
        return error_response(exc)


@router.put("/{project_id}")
async def update_project_endpoint(
    project_id: str,
    body: ProjectUpdate,
    db=Depends(get_db_session),
    current_user: dict = Depends(require_tenant),
):
    """Update an existing project. Requires tenant context."""
    try:
        organization_id = current_user.get("organization_id")
        updated_by = current_user.get("sub")
        project = await update_project_svc(
            db, org_id=organization_id, project_id=project_id, data=body, updated_by=updated_by
        )
        return success_response(data=project, message="Project updated")
    except BuildCoreError as exc:
        return error_response(exc)


@router.delete("/{project_id}")
async def delete_project_endpoint(
    project_id: str,
    db=Depends(get_db_session),
    _current_user: dict = Depends(require_super_admin),
):
    """Soft-delete a project (super admin only)."""
    try:
        organization_id = _current_user.get("organization_id")
        await delete_project_svc(db, org_id=organization_id, project_id=project_id)
        return success_response(message="Project deleted")
    except BuildCoreError as exc:
        return error_response(exc)
