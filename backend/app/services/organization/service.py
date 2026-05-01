"""Organization service layer — business logic and validation.

Validates slug uniqueness, raises BuildCoreError variants on failure,
and returns Pydantic response schemas.
"""

from app.core.exceptions import ConflictError, NotFoundError
from app.schemas.organization import OrganizationCreate, OrganizationResponse, OrganizationUpdate
from app.services.organization import crud


async def get_organization(db, org_id: str) -> OrganizationResponse:
    """Get an organization by ID.

    Args:
        db: Async database session.
        org_id: UUID string of the organization.

    Returns:
        OrganizationResponse schema.

    Raises:
        NotFoundError: If the organization does not exist.
    """
    org = await crud.get_org_by_id(db, org_id)
    if org is None:
        raise NotFoundError(message="Organization not found")
    return OrganizationResponse.model_validate(org)


async def list_organizations(
    db,
    page: int = 1,
    per_page: int = 20,
) -> dict:
    """List organizations with pagination.

    Args:
        db: Async database session.
        page: 1-based page index.
        per_page: Items per page.

    Returns:
        Dict with items, pagination metadata.
    """
    items, total = await crud.list_orgs(db, page, per_page)
    total_pages = (total + per_page - 1) // per_page if per_page > 0 else 0
    return {
        "items": [OrganizationResponse.model_validate(o) for o in items],
        "page": page,
        "per_page": per_page,
        "total": total,
        "total_pages": total_pages,
    }


async def create_organization(db, data: OrganizationCreate) -> OrganizationResponse:
    """Create a new organization with slug-uniqueness validation.

    Args:
        db: Async database session.
        data: Validated OrganizationCreate payload.

    Returns:
        OrganizationResponse schema for the newly created org.

    Raises:
        ConflictError: If an organization with the same slug already exists.
    """
    existing = await crud.get_org_by_slug(db, data.slug)
    if existing is not None:
        raise ConflictError(
            message="Organization with this slug already exists",
            details={"slug": data.slug},
        )

    org = await crud.create_org(
        db,
        name=data.name,
        slug=data.slug,
        address=data.address,
        phone=data.phone,
        email=data.email,
        website=data.website,
        reg_number=data.reg_number,
        currency_code=data.currency_code,
        timezone=data.timezone,
    )
    return OrganizationResponse.model_validate(org)


async def update_organization(
    db,
    org_id: str,
    data: OrganizationUpdate,
) -> OrganizationResponse:
    """Update an existing organization.

    Args:
        db: Async database session.
        org_id: UUID string of the organization.
        data: Validated OrganizationUpdate payload.

    Returns:
        OrganizationResponse schema.

    Raises:
        NotFoundError: If the organization does not exist.
        ConflictError: If the new slug conflicts with another org.
    """
    org = await crud.get_org_by_id(db, org_id)
    if org is None:
        raise NotFoundError(message="Organization not found")

    # Slug uniqueness check (only if slug is being changed)
    if data.slug is not None and data.slug != org.slug:
        existing = await crud.get_org_by_slug(db, data.slug)
        if existing is not None:
            raise ConflictError(
                message="Organization with this slug already exists",
                details={"slug": data.slug},
            )

    update_data = data.model_dump(exclude_unset=True)
    updated = await crud.update_org(db, org_id, **update_data)
    return OrganizationResponse.model_validate(updated)


async def delete_organization(db, org_id: str) -> None:
    """Soft-delete an organization.

    Args:
        db: Async database session.
        org_id: UUID string of the organization.

    Raises:
        NotFoundError: If the organization does not exist.
    """
    deleted = await crud.delete_org(db, org_id)
    if not deleted:
        raise NotFoundError(message="Organization not found")
