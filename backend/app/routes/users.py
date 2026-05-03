"""
BuildCore User Routes.

Endpoints for viewing, updating, deactivating, and deleting users.
Tenant-scoped list; super admin for hard delete and cross-org queries.
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.core.exceptions import BuildCoreError, ForbiddenError
from app.core.pagination import get_pagination_params, compute_offset
from app.core.responses import error_response, paginated_response, success_response
from app.core.dependencies import get_current_user, require_super_admin, require_tenant, get_db_session
from app.schemas.user import UserUpdate, SuperAdminCreateUserRequest
from app.services.user.service import (
    get_user,
    list_users,
    update_user_profile,
    deactivate_user,
    activate_user,
    delete_user,
)
from app.services.auth.crud import get_user_by_email

router = APIRouter(prefix="/users", tags=["Users"])


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
async def list_users_endpoint(
    db=Depends(get_db_session),
    pagination=Depends(get_pagination_params),
    current_user: dict = Depends(get_current_user),
    organization_id: Optional[str] = Query(default=None, description="Org ID (superadmin only)"),
):
    """List users within an organization. Super admin can query any org via ?organization_id=."""
    try:
        org_id = _resolve_org_id(current_user, organization_id)
        offset = compute_offset(pagination)
        users, total = await list_users(
            db, organization_id=org_id, offset=offset, limit=pagination.per_page,
        )
        return paginated_response(
            data=users,
            page=pagination.page,
            per_page=pagination.per_page,
            total=total,
            message="Users retrieved",
        )
    except BuildCoreError as exc:
        return error_response(exc)


@router.post("/create")
async def create_user_endpoint(
    body: SuperAdminCreateUserRequest,
    db=Depends(get_db_session),
    current_user: dict = Depends(require_super_admin),
):
    """Create a user for any organization (super admin only).

    Super admin can create active users with a password directly,
    or create users who will need to set their password later.
    """
    try:
        from app.core.exceptions import ConflictError
        from app.services.auth.crud import create_user
        from app.core.security import get_password_hash
        from datetime import datetime, timezone

        # Check email uniqueness
        existing = await get_user_by_email(db, body.email)
        if existing is not None:
            raise ConflictError(
                message="A user with this email already exists",
                details={"email": body.email},
            )

        user = await create_user(
            db,
            organization_id=body.organization_id,
            email=body.email,
            password_hash=get_password_hash(body.password),
            first_name=body.first_name,
            last_name=body.last_name,
            phone=body.phone,
            role_id=body.role_id,
            is_active=body.is_active,
            email_verified_at=datetime.now(timezone.utc) if body.is_active else None,
            invited_by=current_user.get("sub"),
        )

        return success_response(
            data={"id": user.id, "email": user.email, "is_active": user.is_active},
            message="User created successfully",
        )
    except BuildCoreError as exc:
        return error_response(exc)


@router.get("/{user_id}")
async def get_user_endpoint(
    user_id: str,
    db=Depends(get_db_session),
    _current_user: dict = Depends(get_current_user),
):
    """Retrieve a single user by ID. Requires authentication."""
    try:
        user = await get_user(db, user_id)
        return success_response(data=user, message="User retrieved")
    except BuildCoreError as exc:
        return error_response(exc)


@router.put("/{user_id}")
async def update_user_endpoint(
    user_id: str,
    body: UserUpdate,
    db=Depends(get_db_session),
    _current_user: dict = Depends(require_tenant),
):
    """Update a user's profile. Requires tenant context."""
    try:
        user = await update_user_profile(db, user_id, body)
        return success_response(data=user, message="User updated")
    except BuildCoreError as exc:
        return error_response(exc)


@router.delete("/{user_id}")
async def delete_user_endpoint(
    user_id: str,
    db=Depends(get_db_session),
    _current_user: dict = Depends(require_super_admin),
):
    """Soft-delete a user (super admin only)."""
    try:
        await delete_user(db, user_id)
        return success_response(message="User deleted")
    except BuildCoreError as exc:
        return error_response(exc)


@router.patch("/{user_id}/deactivate")
async def deactivate_user_endpoint(
    user_id: str,
    db=Depends(get_db_session),
    _current_user: dict = Depends(require_tenant),
):
    """Deactivate a user account. Requires tenant context."""
    try:
        user = await deactivate_user(db, user_id)
        return success_response(data=user, message="User deactivated")
    except BuildCoreError as exc:
        return error_response(exc)


@router.patch("/{user_id}/activate")
async def activate_user_endpoint(
    user_id: str,
    db=Depends(get_db_session),
    _current_user: dict = Depends(require_tenant),
):
    """Activate a user account. Requires tenant context."""
    try:
        user = await activate_user(db, user_id)
        return success_response(data=user, message="User activated")
    except BuildCoreError as exc:
        return error_response(exc)
