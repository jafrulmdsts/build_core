"""
BuildCore Organization Routes.

CRUD endpoints for managing organizations. Super admin required for
create/delete; tenant context required for read/update.
"""

from fastapi import APIRouter, Depends

from app.core.exceptions import BuildCoreError
from app.core.pagination import get_pagination_params, compute_offset
from app.core.responses import error_response, paginated_response, success_response
from app.core.dependencies import get_current_user, require_super_admin, require_tenant, get_db_session
from app.schemas.organization import OrganizationCreate, OrganizationUpdate
from app.services.organization.service import (
    get_organization,
    list_organizations,
    create_organization,
    update_organization,
    delete_organization,
)

router = APIRouter(prefix="/organizations", tags=["Organizations"])


@router.get("/")
async def list_organizations_endpoint(
    db=Depends(get_db_session),
    pagination=Depends(get_pagination_params),
    _current_user: dict = Depends(require_super_admin),
):
    """List all organizations (super admin only). Supports pagination."""
    try:
        result = await list_organizations(db, page=pagination.page, per_page=pagination.per_page)
        return paginated_response(
            data=result["items"],
            page=pagination.page,
            per_page=pagination.per_page,
            total=result["total"],
            message="Organizations retrieved",
        )
    except BuildCoreError as exc:
        return error_response(exc)


@router.post("/")
async def create_organization_endpoint(
    body: OrganizationCreate,
    db=Depends(get_db_session),
    _current_user: dict = Depends(require_super_admin),
):
    """Create a new organization (super admin only)."""
    try:
        org = await create_organization(db, body)
        return success_response(data=org, message="Organization created", status_code=201)
    except BuildCoreError as exc:
        return error_response(exc)


@router.get("/{org_id}")
async def get_organization_endpoint(
    org_id: str,
    db=Depends(get_db_session),
    _current_user: dict = Depends(require_tenant),
):
    """Retrieve a single organization by ID. Requires tenant context."""
    try:
        org = await get_organization(db, org_id)
        return success_response(data=org, message="Organization retrieved")
    except BuildCoreError as exc:
        return error_response(exc)


@router.put("/{org_id}")
async def update_organization_endpoint(
    org_id: str,
    body: OrganizationUpdate,
    db=Depends(get_db_session),
    _current_user: dict = Depends(require_tenant),
):
    """Update an existing organization. Requires tenant context."""
    try:
        org = await update_organization(db, org_id, body)
        return success_response(data=org, message="Organization updated")
    except BuildCoreError as exc:
        return error_response(exc)


@router.delete("/{org_id}")
async def delete_organization_endpoint(
    org_id: str,
    db=Depends(get_db_session),
    _current_user: dict = Depends(require_super_admin),
):
    """Soft-delete an organization (super admin only)."""
    try:
        await delete_organization(db, org_id)
        return success_response(message="Organization deleted")
    except BuildCoreError as exc:
        return error_response(exc)
