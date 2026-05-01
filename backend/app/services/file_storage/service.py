"""File Storage service layer — business logic for file attachment records.

Provides listing by entity, creation, and deletion of file records.
Does NOT handle actual file upload/download — that is left to a
dedicated storage service or presigned URLs.
"""

from app.core.exceptions import NotFoundError, ValidationError
from app.schemas.file_attachment import FileAttachmentCreate, FileAttachmentResponse
from app.services.file_storage import crud

VALID_ENTITY_TYPES = {"project", "employee", "contractor", "expense"}


async def list_files(
    db,
    org_id: str,
    page: int = 1,
    per_page: int = 20,
    entity_type: str | None = None,
    entity_id: str | None = None,
) -> dict:
    """List file attachments for an organization with optional filters.

    Args:
        db: Async database session.
        org_id: UUID string of the organization.
        page: 1-based page index.
        per_page: Items per page.
        entity_type: Optional entity type filter.
        entity_id: Optional entity ID filter.

    Returns:
        Dict with items list and pagination metadata.
    """
    items, total = await crud.list_files_by_org(
        db, org_id, page, per_page,
        entity_type=entity_type,
        entity_id=entity_id,
    )
    total_pages = (total + per_page - 1) // per_page if per_page > 0 else 0
    return {
        "items": [FileAttachmentResponse.model_validate(f) for f in items],
        "page": page,
        "per_page": per_page,
        "total": total,
        "total_pages": total_pages,
    }


async def create_file(
    db, org_id: str, data: FileAttachmentCreate
) -> FileAttachmentResponse:
    """Create a new file attachment record.

    Validates the entity_type against allowed values.

    Args:
        db: Async database session.
        org_id: UUID string of the organization.
        data: Validated FileAttachmentCreate payload.

    Returns:
        FileAttachmentResponse schema for the new record.

    Raises:
        ValidationError: If entity_type is not in the allowed set.
    """
    if data.entity_type not in VALID_ENTITY_TYPES:
        raise ValidationError(
            message=f"Invalid entity_type. Must be one of: {sorted(VALID_ENTITY_TYPES)}",
            details={"entity_type": data.entity_type},
        )

    file_record = await crud.create_file(
        db,
        organization_id=org_id,
        entity_type=data.entity_type,
        entity_id=data.entity_id,
        file_name=data.file_name,
        original_name=data.original_name,
        file_path=data.file_path,
        file_type=data.file_type,
        mime_type=data.mime_type,
        file_size=data.file_size,
        uploaded_by=data.uploaded_by,
    )
    return FileAttachmentResponse.model_validate(file_record)


async def delete_file(db, org_id: str, file_id: str) -> None:
    """Delete a file attachment record.

    Args:
        db: Async database session.
        org_id: UUID string of the organization.
        file_id: UUID string of the file attachment.

    Raises:
        NotFoundError: If the file record does not exist.
    """
    success = await crud.delete_file(db, file_id, org_id)
    if not success:
        raise NotFoundError(message="File attachment not found")
