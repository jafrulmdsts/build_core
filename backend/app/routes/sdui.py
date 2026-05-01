"""
BuildCore SDUI (Server-Driven UI) Routes.

Endpoints that return navigation structure and UI configuration
computed server-side based on the authenticated user's permissions.
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.core.exceptions import BuildCoreError
from app.core.responses import error_response, success_response
from app.core.dependencies import get_current_user, get_db_session
from app.services.sdui.service import get_navigation

router = APIRouter(prefix="/sdui", tags=["SDUI"])


@router.get("/navigation")
async def get_navigation_endpoint(
    db=Depends(get_db_session),
    current_user: dict = Depends(get_current_user),
    menu_type: Optional[str] = Query(
        default="sidebar",
        description="Type of navigation menu to retrieve (sidebar, header, etc.)",
    ),
):
    """Get the navigation tree for the authenticated user.

    Returns a hierarchical list of menu items filtered by the user's
    effective permissions and the requested menu type.
    """
    try:
        navigation = await get_navigation(db, current_user, menu_type)
        return success_response(data=navigation, message="Navigation retrieved")
    except BuildCoreError as exc:
        return error_response(exc)
