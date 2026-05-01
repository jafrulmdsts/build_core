"""
BuildCore Audit Log Routes.

Read-only endpoint for querying the immutable audit trail.
Requires tenant context so logs are scoped to the organization.
"""

from fastapi import APIRouter, Depends

from app.core.exceptions import BuildCoreError
from app.core.pagination import get_pagination_params, compute_offset
from app.core.responses import error_response, paginated_response
from app.core.dependencies import require_tenant, get_db_session
from app.services.audit.service import get_audit_logs

router = APIRouter(prefix="/audit-logs", tags=["Audit"])


@router.get("/")
async def list_audit_logs_endpoint(
    db=Depends(get_db_session),
    pagination=Depends(get_pagination_params),
    current_user: dict = Depends(require_tenant),
):
    """List audit logs for the authenticated organization. Supports pagination."""
    try:
        organization_id = current_user.get("organization_id")
        offset = compute_offset(pagination)
        logs, total = await get_audit_logs(
            db, organization_id=organization_id, offset=offset, limit=pagination.per_page,
        )
        return paginated_response(
            data=logs,
            page=pagination.page,
            per_page=pagination.per_page,
            total=total,
            message="Audit logs retrieved",
        )
    except BuildCoreError as exc:
        return error_response(exc)
