"""SDUI service layer — permission-filtered navigation tree.

Returns only menu items the user has permission to see.
"""

from app.schemas.sdui import SduiMenuResponse
from app.services.sdui import crud


def _filter_tree_by_permissions(
    nodes: list[dict],
    user_permissions: list[str],
) -> list[SduiMenuResponse]:
    """Recursively filter a menu tree by user permissions.

    A node is included if:
    - It has no permission_key (public), OR
    - Its permission_key is in user_permissions.

    Parent nodes are kept if at least one descendant passes the filter.

    Args:
        nodes: List of tree node dicts from crud.get_menu_tree.
        user_permissions: List of permission keys the user holds.

    Returns:
        List of SduiMenuResponse with filtered children.
    """
    result: list[SduiMenuResponse] = []

    for node in nodes:
        permission_key = node.get("permission_key")
        has_access = permission_key is None or permission_key in user_permissions

        # Recursively filter children
        children = _filter_tree_by_permissions(
            node.get("children", []),
            user_permissions,
        )

        # Include node if it has access or has accessible children
        if has_access or children:
            result.append(
                SduiMenuResponse(
                    id=node["id"],
                    parent_id=node["parent_id"],
                    label_key=node["label_key"],
                    label_en=node["label_en"],
                    label_bn=node["label_bn"],
                    icon=node["icon"],
                    route_path=node["route_path"],
                    api_endpoint=node["api_endpoint"],
                    permission_key=node["permission_key"],
                    sort_order=node["sort_order"],
                    is_visible=node["is_visible"],
                    target=node["target"],
                    menu_type=node["menu_type"],
                    children=children,
                    created_at=node["created_at"],
                )
            )

    return result


async def get_navigation(
    db,
    user_permissions: list[str],
    menu_type: str = "sidebar",
) -> list[SduiMenuResponse]:
    """Get the permission-filtered navigation tree for a user.

    Args:
        db: Async database session.
        user_permissions: List of permission keys the user holds.
        menu_type: Type of menu (default "sidebar").

    Returns:
        List of SduiMenuResponse nodes forming the navigation tree.
    """
    tree = await crud.get_menu_tree(db, menu_type)
    return _filter_tree_by_permissions(tree, user_permissions)
