"""Role service layer — business logic, validation, and permission resolution.

Handles slug-uniqueness checks, system-role protection, permission
override creation, and effective permission computation.
"""

import json

from app.core.exceptions import (
    BuildCoreError,
    ConflictError,
    NotFoundError,
    ValidationError,
)
from app.models.role import Role
from app.models.user import User
from app.models.user_permission_override import UserPermissionOverride
from app.schemas.role import (
    PermissionOverrideCreate,
    PermissionOverrideResponse,
    RoleCreate,
    RoleResponse,
    RoleUpdate,
)
from app.services.role import crud
from sqlalchemy import select


def _parse_permissions(permissions_text: str | None) -> list[str]:
    """Safely parse a JSON-encoded permissions string into a list."""
    if not permissions_text:
        return []
    try:
        parsed = json.loads(permissions_text)
        if isinstance(parsed, list):
            return [str(p) for p in parsed]
        return []
    except (json.JSONDecodeError, TypeError):
        return []


async def get_role(db, role_id: str) -> RoleResponse:
    """Get a role by ID.

    Args:
        db: Async database session.
        role_id: UUID string of the role.

    Returns:
        RoleResponse schema.

    Raises:
        NotFoundError: If the role does not exist.
    """
    role = await crud.get_role_by_id(db, role_id)
    if role is None:
        raise NotFoundError(message="Role not found")

    data = RoleResponse.model_validate(role)
    data.permissions = _parse_permissions(role.permissions)
    return data


async def list_roles(
    db,
    organization_id: str,
    page: int = 1,
    per_page: int = 20,
) -> dict:
    """List roles available to an organization with pagination.

    Includes org-specific roles plus system roles.

    Args:
        db: Async database session.
        organization_id: UUID string of the organization.
        page: 1-based page index.
        per_page: Items per page.

    Returns:
        Dict with items, pagination metadata.
    """
    items, total = await crud.list_roles(db, organization_id, page, per_page)
    total_pages = (total + per_page - 1) // per_page if per_page > 0 else 0

    response_items = []
    for role in items:
        data = RoleResponse.model_validate(role)
        data.permissions = _parse_permissions(role.permissions)
        response_items.append(data)

    return {
        "items": response_items,
        "page": page,
        "per_page": per_page,
        "total": total,
        "total_pages": total_pages,
    }


async def create_role(
    db,
    org_id: str,
    data: RoleCreate,
) -> RoleResponse:
    """Create a new organization-scoped role.

    Validates slug uniqueness within the organization.

    Args:
        db: Async database session.
        org_id: UUID string of the organization.
        data: Validated RoleCreate payload.

    Returns:
        RoleResponse schema.

    Raises:
        ConflictError: If a role with the same slug exists in the org.
    """
    # Check slug uniqueness within the org
    stmt = select(Role).where(
        Role.organization_id == org_id,
        Role.slug == data.slug,
        Role.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    if result.scalar_one_or_none() is not None:
        raise ConflictError(
            message="Role with this slug already exists in the organization",
            details={"slug": data.slug},
        )

    role = await crud.create_role(
        db,
        organization_id=org_id,
        name=data.name,
        slug=data.slug,
        description=data.description,
        permissions=data.permissions,
        is_system_role=False,
        is_active=True,
    )
    response = RoleResponse.model_validate(role)
    response.permissions = data.permissions
    return response


async def update_role(
    db,
    role_id: str,
    data: RoleUpdate,
) -> RoleResponse:
    """Update an existing role.

    Refuses to modify system roles.

    Args:
        db: Async database session.
        role_id: UUID string of the role.
        data: Validated RoleUpdate payload.

    Returns:
        RoleResponse schema.

    Raises:
        NotFoundError: If the role does not exist.
        BuildCoreError: If the role is a system role.
        ConflictError: If slug change conflicts.
    """
    role = await crud.get_role_by_id(db, role_id)
    if role is None:
        raise NotFoundError(message="Role not found")
    if role.is_system_role:
        raise BuildCoreError(
            code="FORBIDDEN",
            message="Cannot modify a system role",
            status_code=403,
        )

    # Slug uniqueness check
    if data.slug is not None and data.slug != role.slug:
        stmt = select(Role).where(
            Role.organization_id == role.organization_id,
            Role.slug == data.slug,
            Role.deleted_at.is_(None),
            Role.id != role_id,
        )
        result = await db.execute(stmt)
        if result.scalar_one_or_none() is not None:
            raise ConflictError(
                message="Role with this slug already exists in the organization",
                details={"slug": data.slug},
            )

    update_data = data.model_dump(exclude_unset=True)
    updated = await crud.update_role(db, role_id, **update_data)

    response = RoleResponse.model_validate(updated)
    if data.permissions is not None:
        response.permissions = data.permissions
    else:
        response.permissions = _parse_permissions(updated.permissions)
    return response


async def delete_role(db, role_id: str) -> None:
    """Soft-delete a role.

    Refuses to delete system roles.

    Args:
        db: Async database session.
        role_id: UUID string of the role.

    Raises:
        NotFoundError: If the role does not exist.
        BuildCoreError: If the role is a system role.
    """
    role = await crud.get_role_by_id(db, role_id)
    if role is None:
        raise NotFoundError(message="Role not found")
    if role.is_system_role:
        raise BuildCoreError(
            code="FORBIDDEN",
            message="Cannot delete a system role",
            status_code=403,
        )

    await crud.delete_role(db, role_id)


async def create_permission_override(
    db,
    data: PermissionOverrideCreate,
    granted_by: str,
) -> PermissionOverrideResponse:
    """Create a user permission override.

    Validates that the target user exists.

    Args:
        db: Async database session.
        data: Validated PermissionOverrideCreate payload.
        granted_by: UUID string of the admin granting the override.

    Returns:
        PermissionOverrideResponse schema.

    Raises:
        NotFoundError: If the target user does not exist.
    """
    # Validate user exists
    user_stmt = select(User).where(
        User.id == data.user_id,
        User.deleted_at.is_(None),
    )
    user_result = await db.execute(user_stmt)
    if user_result.scalar_one_or_none() is None:
        raise NotFoundError(message="User not found")

    override = UserPermissionOverride(
        user_id=data.user_id,
        permission_key=data.permission_key,
        is_granted=data.is_granted,
        granted_by=granted_by,
        reason=data.reason,
        expires_at=data.expires_at,
    )
    db.add(override)
    await db.flush()

    return PermissionOverrideResponse.model_validate(override)


async def get_user_permissions(db, user_id: str) -> list[str]:
    """Compute the effective permission list for a user.

    Combines role permissions with per-user overrides:
    1. Get user's role permissions as a set.
    2. Apply grant overrides (add to set).
    3. Apply revoke overrides (remove from set).

    Args:
        db: Async database session.
        user_id: UUID string of the user.

    Returns:
        Sorted list of effective permission key strings.
    """
    # Get user
    user_stmt = select(User).where(
        User.id == user_id,
        User.deleted_at.is_(None),
    )
    user_result = await db.execute(user_stmt)
    user = user_result.scalar_one_or_none()
    if user is None:
        return []

    # Start with role permissions
    permissions: set[str] = set()

    if user.role_id:
        role_stmt = select(Role).where(
            Role.id == user.role_id,
            Role.deleted_at.is_(None),
            Role.is_active.is_(True),
        )
        role_result = await db.execute(role_stmt)
        role = role_result.scalar_one_or_none()
        if role:
            permissions.update(_parse_permissions(role.permissions))

    # Apply overrides
    overrides = await crud.get_permission_overrides(db, user_id)
    for override in overrides:
        if override.is_granted:
            permissions.add(override.permission_key)
        else:
            permissions.discard(override.permission_key)

    return sorted(permissions)
