"""
BuildCore User Routes.

Endpoints for viewing, updating, deactivating, and deleting users.
Tenant-scoped list; super admin for hard delete.
"""

from fastapi import APIRouter, Depends

from app.core.exceptions import BuildCoreError
from app.core.pagination import get_pagination_params, compute_offset
from app.core.responses import error_response, paginated_response, success_response
from app.core.dependencies import get_current_user, require_super_admin, require_tenant, get_db_session
from app.schemas.user import UserUpdate
from app.services.user.service import (
    get_user,
    list_users,
    update_user_profile,
    deactivate_user,
    activate_user,
    delete_user,
)

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/")
async def list_users_endpoint(
    db=Depends(get_db_session),
    pagination=Depends(get_pagination_params),
    current_user: dict = Depends(require_tenant),
):
    """List users within the authenticated organization. Supports pagination."""
    try:
        organization_id = current_user.get("organization_id")
        offset = compute_offset(pagination)
        users, total = await list_users(
            db, organization_id=organization_id, offset=offset, limit=pagination.per_page,
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
