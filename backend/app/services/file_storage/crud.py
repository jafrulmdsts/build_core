"""File Attachment CRUD operations — low-level database access.

Files do not use soft-delete. Records are hard-deleted since
actual storage cleanup is handled separately.
"""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.file_attachment import FileAttachment


async def get_file_by_id(
    db: AsyncSession, file_id: str, org_id: str
) -> FileAttachment | None:
    """Fetch a single file attachment by ID scoped to an organization.

    Args:
        db: Async database session.
        file_id: UUID string of the file attachment.
        org_id: UUID string of the organization.

    Returns:
        FileAttachment row or None if not found.
    """
    stmt = select(FileAttachment).where(
        FileAttachment.id == file_id,
        FileAttachment.organization_id == org_id,
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def list_files_by_org(
    db: AsyncSession,
    org_id: str,
    page: int = 1,
    per_page: int = 20,
    entity_type: str | None = None,
    entity_id: str | None = None,
) -> tuple[list[FileAttachment], int]:
    """List file attachments for an organization with pagination and filters.

    Args:
        db: Async database session.
        org_id: UUID string of the organization.
        page: 1-based page index.
        per_page: Items per page.
        entity_type: Optional entity type filter.
        entity_id: Optional entity ID filter.

    Returns:
        Tuple of (items, total_count).
    """
    filters = [FileAttachment.organization_id == org_id]

    if entity_type is not None:
        filters.append(FileAttachment.entity_type == entity_type)
    if entity_id is not None:
        filters.append(FileAttachment.entity_id == entity_id)

    # Count
    count_stmt = select(func.count()).select_from(FileAttachment).where(*filters)
    total = (await db.execute(count_stmt)).scalar_one()

    # Fetch page
    offset = (page - 1) * per_page
    stmt = (
        select(FileAttachment)
        .where(*filters)
        .order_by(FileAttachment.created_at.desc())
        .offset(offset)
        .limit(per_page)
    )
    result = await db.execute(stmt)
    items = list(result.scalars().all())

    return items, total


async def create_file(db: AsyncSession, **kwargs: object) -> FileAttachment:
    """Create a new file attachment record and flush to the session.

    Args:
        db: Async database session.
        **kwargs: Column values for the new FileAttachment.

    Returns:
        The new FileAttachment instance (id populated after flush).
    """
    file_record = FileAttachment(**kwargs)
    db.add(file_record)
    await db.flush()
    return file_record


async def delete_file(db: AsyncSession, file_id: str, org_id: str) -> bool:
    """Hard-delete a file attachment record.

    Args:
        db: Async database session.
        file_id: UUID string of the file attachment.
        org_id: UUID string of the organization.

    Returns:
        True if the record was found and deleted, False otherwise.
    """
    stmt = select(FileAttachment).where(
        FileAttachment.id == file_id,
        FileAttachment.organization_id == org_id,
    )
    result = await db.execute(stmt)
    file_record = result.scalar_one_or_none()
    if file_record is None:
        return False

    await db.delete(file_record)
    await db.flush()
    return True
