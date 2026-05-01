"""
Seed default SDUI menu items.

Creates the sidebar navigation entries rendered by the server-driven UI.
Each item carries both English and Bengali labels for i18n support.
"""

import json

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sdui_menu import SduiMenu

DEFAULT_MENUS: list[dict] = [
    {
        "id": "00000000-0000-4000-b000-000000000001",
        "parent_id": None,
        "label_key": "dashboard",
        "label_en": "Dashboard",
        "label_bn": "ড্যাশবোর্ড",
        "icon": "LayoutDashboard",
        "route_path": "/dashboard",
        "api_endpoint": None,
        "permission_key": None,
        "sort_order": 1,
        "is_visible": True,
        "target": "_self",
        "menu_type": "sidebar",
    },
    {
        "id": "00000000-0000-4000-b000-000000000002",
        "parent_id": None,
        "label_key": "projects",
        "label_en": "Projects",
        "label_bn": "প্রকল্পসমূহ",
        "icon": "Building2",
        "route_path": "/projects",
        "api_endpoint": None,
        "permission_key": "project.view",
        "sort_order": 2,
        "is_visible": True,
        "target": "_self",
        "menu_type": "sidebar",
    },
    {
        "id": "00000000-0000-4000-b000-000000000003",
        "parent_id": None,
        "label_key": "employees",
        "label_en": "Employees",
        "label_bn": "কর্মীবৃন্দ",
        "icon": "Users",
        "route_path": "/employees",
        "api_endpoint": None,
        "permission_key": "employee.view",
        "sort_order": 3,
        "is_visible": True,
        "target": "_self",
        "menu_type": "sidebar",
    },
    {
        "id": "00000000-0000-4000-b000-000000000004",
        "parent_id": None,
        "label_key": "contractors",
        "label_en": "Contractors",
        "label_bn": "চুক্তিকর্তা",
        "icon": "HardHat",
        "route_path": "/contractors",
        "api_endpoint": None,
        "permission_key": "contractor.view",
        "sort_order": 4,
        "is_visible": True,
        "target": "_self",
        "menu_type": "sidebar",
    },
    {
        "id": "00000000-0000-4000-b000-000000000005",
        "parent_id": None,
        "label_key": "expenses",
        "label_en": "Expenses",
        "label_bn": "ব্যয়সমূহ",
        "icon": "Receipt",
        "route_path": "/expenses",
        "api_endpoint": None,
        "permission_key": "expense.view",
        "sort_order": 5,
        "is_visible": True,
        "target": "_self",
        "menu_type": "sidebar",
    },
    {
        "id": "00000000-0000-4000-b000-000000000006",
        "parent_id": None,
        "label_key": "reports",
        "label_en": "Reports",
        "label_bn": "প্রতিবেদনসমূহ",
        "icon": "BarChart3",
        "route_path": "/reports",
        "api_endpoint": None,
        "permission_key": "report.view",
        "sort_order": 6,
        "is_visible": True,
        "target": "_self",
        "menu_type": "sidebar",
    },
    {
        "id": "00000000-0000-4000-b000-000000000007",
        "parent_id": None,
        "label_key": "settings",
        "label_en": "Settings",
        "label_bn": "সেটিংস",
        "icon": "Settings",
        "route_path": "/settings",
        "api_endpoint": None,
        "permission_key": "settings.view",
        "sort_order": 7,
        "is_visible": True,
        "target": "_self",
        "menu_type": "sidebar",
    },
]


async def seed_sdui_menus(db: AsyncSession) -> None:
    """Insert default SDUI menu items if they don't already exist.

    Args:
        db: Active async database session.
    """
    for menu_data in DEFAULT_MENUS:
        stmt = select(SduiMenu).where(SduiMenu.id == menu_data["id"])
        result = await db.execute(stmt)
        if result.scalar_one_or_none() is None:
            db.add(SduiMenu(**menu_data))
    await db.flush()
