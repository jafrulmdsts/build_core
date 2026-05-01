"""User service layer — business logic and validation.

Validates cross-entity references (e.g. role_id) at service layer,
raises BuildCoreError variants on failure.
"""

from app.core.exceptions import NotFoundError, ValidationError
from app.models.role import Role
from app.schemas.user import UserResponse, UserUpdate
from app.services.role import crud as role_crud
from app.services.user import crud


async def get_user(db, user_id: str) -> UserResponse:
    """Get a user by ID.

    Args:
        db: Async database session.
        user_id: UUID string of the user.

    Returns:
        UserResponse schema.

    Raises:
        NotFoundError: If the user does not exist.
    """
    user = await crud.get_user_by_id(db, user_id)
    if user is None:
        raise NotFoundError(message="User not found")
    return UserResponse.model_validate(user)


async def list_users(
    db,
    organization_id: str,
    page: int = 1,
    per_page: int = 20,
) -> dict:
    """List users in an organization with pagination.

    Args:
        db: Async database session.
        organization_id: UUID string of the organization.
        page: 1-based page index.
        per_page: Items per page.

    Returns:
        Dict with items, pagination metadata.
    """
    items, total = await crud.list_users_by_org(db, organization_id, page, per_page)
    total_pages = (total + per_page - 1) // per_page if per_page > 0 else 0
    return {
        "items": [UserResponse.model_validate(u) for u in items],
        "page": page,
        "per_page": per_page,
        "total": total,
        "total_pages": total_pages,
    }


async def update_user_profile(
    db,
    user_id: str,
    data: UserUpdate,
) -> UserResponse:
    """Update a user's profile fields.

    If role_id is provided, validates that the role exists and is active.

    Args:
        db: Async database session.
        user_id: UUID string of the user.
        data: Validated UserUpdate payload.

    Returns:
        UserResponse schema.

    Raises:
        NotFoundError: If the user does not exist.
        ValidationError: If the provided role_id is invalid or inactive.
    """
    user = await crud.get_user_by_id(db, user_id)
    if user is None:
        raise NotFoundError(message="User not found")

    # Validate role_id if provided
    if data.role_id is not None:
        from sqlalchemy import select

        from app.database import Base as DBBase

        stmt = select(Role).where(
            Role.id == data.role_id,
            Role.deleted_at.is_(None),
            Role.is_active.is_(True),
        )
        result = await db.execute(stmt)
        role = result.scalar_one_or_none()
        if role is None:
            raise ValidationError(
                message="Invalid or inactive role",
                details={"role_id": data.role_id},
            )

    update_data = data.model_dump(exclude_unset=True)
    updated = await crud.update_user(db, user_id, **update_data)
    return UserResponse.model_validate(updated)


async def deactivate_user(db, user_id: str) -> UserResponse:
    """Deactivate a user (set is_active = False).

    Args:
        db: Async database session.
        user_id: UUID string of the user.

    Returns:
        UserResponse schema.

    Raises:
        NotFoundError: If the user does not exist.
    """
    updated = await crud.update_user(db, user_id, is_active=False)
    if updated is None:
        raise NotFoundError(message="User not found")
    return UserResponse.model_validate(updated)


async def delete_user(db, user_id: str) -> None:
    """Soft-delete a user.

    Args:
        db: Async database session.
        user_id: UUID string of the user.

    Raises:
        NotFoundError: If the user does not exist.
    """
    deleted = await crud.delete_user(db, user_id)
    if not deleted:
        raise NotFoundError(message="User not found")
