"""
BuildCore File Attachment Routes.

Endpoints for managing file attachment records. Does NOT handle
actual file upload/download — records only. Tenant context required.
"""

from fastapi import APIRouter, Depends, Query

from app.core.dependencies import require_tenant, get_db_session
from app.core.exceptions import BuildCoreError
from app.core.pagination import get_pagination_params
from app.core.responses import error_response, paginated_response, success_response
from app.schemas.file_attachment import FileAttachmentCreate
from app.services.file_storage.service import (
    create_file as create_file_svc,
    delete_file as delete_file_svc,
    list_files as list_files_svc,
)

router = APIRouter(prefix="/files", tags=["Files"])


@router.get("/")
async def list_files_endpoint(
    db=Depends(get_db_session),
    pagination=Depends(get_pagination_params),
    current_user: dict = Depends(require_tenant),
    entity_type: str | None = Query(default=None, description="Filter by entity type"),
    entity_id: str | None = Query(default=None, description="Filter by entity ID"),
):
    """List file attachments within the authenticated organization. Supports pagination and filters."""
    try:
        organization_id = current_user.get("organization_id")
        result = await list_files_svc(
            db,
            org_id=organization_id,
            page=pagination.page,
            per_page=pagination.per_page,
            entity_type=entity_type,
            entity_id=entity_id,
        )
        return paginated_response(
            data=result["items"],
            page=result["page"],
            per_page=result["per_page"],
            total=result["total"],
            message="Files retrieved",
        )
    except BuildCoreError as exc:
        return error_response(exc)


@router.post("/")
async def create_file_endpoint(
    body: FileAttachmentCreate,
    db=Depends(get_db_session),
    current_user: dict = Depends(require_tenant),
):
    """Create a new file attachment record within the authenticated organization."""
    try:
        organization_id = current_user.get("organization_id")
        file_record = await create_file_svc(
            db, org_id=organization_id, data=body
        )
        return success_response(data=file_record, message="File record created")
    except BuildCoreError as exc:
        return error_response(exc)


@router.delete("/{file_id}")
async def delete_file_endpoint(
    file_id: str,
    db=Depends(get_db_session),
    current_user: dict = Depends(require_tenant),
):
    """Delete a file attachment record. Requires tenant context."""
    try:
        organization_id = current_user.get("organization_id")
        await delete_file_svc(db, org_id=organization_id, file_id=file_id)
        return success_response(message="File record deleted")
    except BuildCoreError as exc:
        return error_response(exc)
