"""SDUI Menu CRUD operations — low-level database access.

SduiMenu uses hard delete (no deleted_at column). All menu items
are fetched without soft-delete filtering.
"""

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sdui_menu import SduiMenu


async def get_all_menus(
    db: AsyncSession,
    menu_type: str | None = None,
) -> list[SduiMenu]:
    """Fetch all menu items, optionally filtered by menu_type.

    Args:
        db: Async database session.
        menu_type: Optional filter (e.g. "sidebar", "topbar").

    Returns:
        List of all SduiMenu rows, ordered by sort_order.
    """
    stmt = select(SduiMenu).order_by(SduiMenu.sort_order.asc())
    if menu_type is not None:
        stmt = stmt.where(SduiMenu.menu_type == menu_type)

    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_menu_tree(
    db: AsyncSession,
    menu_type: str = "sidebar",
) -> list[dict[str, Any]]:
    """Build a tree structure from flat menu items.

    Root items (parent_id IS NULL) become top-level nodes.
    Child items are nested under their parent.

    Args:
        db: Async database session.
        menu_type: Filter menus by type (default "sidebar").

    Returns:
        List of tree-structured dicts with a "children" key.
    """
    all_menus = await get_all_menus(db, menu_type)

    # Index by id for quick lookup
    menu_map: dict[str, dict[str, Any]] = {}
    for menu in all_menus:
        menu_map[menu.id] = {
            "id": menu.id,
            "parent_id": menu.parent_id,
            "label_key": menu.label_key,
            "label_en": menu.label_en,
            "label_bn": menu.label_bn,
            "icon": menu.icon,
            "route_path": menu.route_path,
            "api_endpoint": menu.api_endpoint,
            "permission_key": menu.permission_key,
            "sort_order": menu.sort_order,
            "is_visible": menu.is_visible,
            "target": menu.target,
            "menu_type": menu.menu_type,
            "created_at": menu.created_at,
            "children": [],
        }

    # Build tree
    roots: list[dict[str, Any]] = []
    for menu_dict in menu_map.values():
        parent_id = menu_dict["parent_id"]
        if parent_id and parent_id in menu_map:
            menu_map[parent_id]["children"].append(menu_dict)
        else:
            roots.append(menu_dict)

    return roots
