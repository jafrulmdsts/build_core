"""
BuildCore Role & Permission Routes.

Endpoints for managing roles, permission overrides, and querying
effective user permissions within an organization.

Super admin can query roles for any organization via ?organization_id= param.
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.core.exceptions import BuildCoreError, ForbiddenError
from app.core.pagination import get_pagination_params, compute_offset
from app.core.responses import error_response, paginated_response, success_response
from app.core.dependencies import require_super_admin, require_tenant, get_current_user, get_db_session
from app.schemas.role import RoleCreate, RoleUpdate, PermissionOverrideCreate
from app.services.role.service import (
    get_role,
    list_roles,
    create_role,
    update_role,
    delete_role,
    create_permission_override,
    get_user_permissions,
)

router = APIRouter(prefix="/roles", tags=["Roles"])


def _resolve_org_id(
    current_user: dict,
    query_org_id: Optional[str] = None,
) -> str:
    """Determine organization_id from JWT or query param (superadmin only).

    Regular users always use their JWT organization_id.
    Superadmins can override via ?organization_id= query param.
    """
    jwt_org = current_user.get("organization_id")
    is_sa = current_user.get("is_super_admin")

    if is_sa and query_org_id:
        return query_org_id

    if jwt_org:
        return jwt_org

    raise ForbiddenError(
        message="No organization context found",
        details={"hint": "Provide organization_id query param or use a tenant user"},
    )


@router.get("/")
async def list_roles_endpoint(
    db=Depends(get_db_session),
    pagination=Depends(get_pagination_params),
    current_user: dict = Depends(get_current_user),
    organization_id: Optional[str] = Query(default=None, description="Org ID (superadmin only)"),
):
    """List roles within an organization. Super admin can query any org via ?organization_id=."""
    try:
        org_id = _resolve_org_id(current_user, organization_id)
        offset = compute_offset(pagination)
        roles, total = await list_roles(
            db, organization_id=org_id, offset=offset, limit=pagination.per_page,
        )
        return paginated_response(
            data=roles,
            page=pagination.page,
            per_page=pagination.per_page,
            total=total,
            message="Roles retrieved",
        )
    except BuildCoreError as exc:
        return error_response(exc)


@router.post("/", status_code=201)
async def create_role_endpoint(
    body: RoleCreate,
    db=Depends(get_db_session),
    current_user: dict = Depends(require_tenant),
):
    """Create a new role within the authenticated organization."""
    try:
        organization_id = current_user.get("organization_id")
        role = await create_role(db, organization_id, body)
        return success_response(data=role, message="Role created")
    except BuildCoreError as exc:
        return error_response(exc)


@router.get("/{role_id}")
async def get_role_endpoint(
    role_id: str,
    db=Depends(get_db_session),
    _current_user: dict = Depends(require_tenant),
):
    """Retrieve a single role by ID. Requires tenant context."""
    try:
        role = await get_role(db, role_id)
        return success_response(data=role, message="Role retrieved")
    except BuildCoreError as exc:
        return error_response(exc)


@router.put("/{role_id}")
async def update_role_endpoint(
    role_id: str,
    body: RoleUpdate,
    db=Depends(get_db_session),
    _current_user: dict = Depends(require_tenant),
):
    """Update an existing role. Requires tenant context."""
    try:
        role = await update_role(db, role_id, body)
        return success_response(data=role, message="Role updated")
    except BuildCoreError as exc:
        return error_response(exc)


@router.delete("/{role_id}")
async def delete_role_endpoint(
    role_id: str,
    db=Depends(get_db_session),
    _current_user: dict = Depends(require_super_admin),
):
    """Delete a role (super admin only)."""
    try:
        await delete_role(db, role_id)
        return success_response(message="Role deleted")
    except BuildCoreError as exc:
        return error_response(exc)


@router.post("/permissions/override", status_code=201)
async def create_permission_override_endpoint(
    body: PermissionOverrideCreate,
    db=Depends(get_db_session),
    current_user: dict = Depends(require_tenant),
):
    """Create a permission override for a specific user.

    Grants or revokes an individual permission, optionally with an
    expiration date and audit reason.
    """
    try:
        override = await create_permission_override(db, body, current_user)
        return success_response(
            data=override, message="Permission override created"
        )
    except BuildCoreError as exc:
        return error_response(exc)


@router.get("/users/{user_id}/permissions")
async def get_user_permissions_endpoint(
    user_id: str,
    db=Depends(get_db_session),
    _current_user: dict = Depends(require_tenant),
):
    """Get the effective permissions for a user.

    Computes the union of role permissions and any individual overrides,
    then returns the final set of granted permission keys.
    """
    try:
        permissions = await get_user_permissions(db, user_id)
        return success_response(data=permissions, message="User permissions retrieved")
    except BuildCoreError as exc:
        return error_response(exc)
