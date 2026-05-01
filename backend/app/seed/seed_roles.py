"""
Seed default system roles.

Idempotent – inserts rows only when the predefined UUID does not already exist.
All system roles have ``organization_id=None`` so they apply globally.
"""

import json

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.role import Role

DEFAULT_ROLES: list[dict] = [
    {
        "id": "00000000-0000-4000-a000-000000000001",
        "organization_id": None,
        "name": "Super Admin",
        "slug": "super_admin",
        "description": "Full system access across all tenants",
        "is_system_role": True,
        "permissions": json.dumps(["*"]),
        "is_active": True,
    },
    {
        "id": "00000000-0000-4000-a000-000000000002",
        "organization_id": None,
        "name": "Organization Admin",
        "slug": "org_admin",
        "description": "Full access within a single organization, except super-admin actions",
        "is_system_role": True,
        "permissions": json.dumps([
            "user.view", "user.create", "user.update", "user.delete", "user.invite",
            "role.view", "role.create", "role.update",
            "org.view", "org.update",
            "project.view", "project.create", "project.update", "project.delete",
            "employee.view", "employee.create", "employee.update", "employee.delete",
            "contractor.view", "contractor.create", "contractor.update", "contractor.delete",
            "expense.view", "expense.create", "expense.update", "expense.delete", "expense.approve",
            "report.view", "report.export",
            "audit.view",
            "settings.view", "settings.update",
            "subscription.view",
        ]),
        "is_active": True,
    },
    {
        "id": "00000000-0000-4000-a000-000000000003",
        "organization_id": None,
        "name": "Project Manager",
        "slug": "project_manager",
        "description": "Manage projects, employees, contractors, and expenses",
        "is_system_role": True,
        "permissions": json.dumps([
            "project.view", "project.create", "project.update", "project.delete",
            "employee.view", "employee.create", "employee.update", "employee.delete",
            "contractor.view", "contractor.create", "contractor.update", "contractor.delete",
            "expense.view", "expense.create", "expense.update", "expense.delete", "expense.approve",
        ]),
        "is_active": True,
    },
    {
        "id": "00000000-0000-4000-a000-000000000004",
        "organization_id": None,
        "name": "Accountant",
        "slug": "accountant",
        "description": "Access to expenses and financial reports",
        "is_system_role": True,
        "permissions": json.dumps([
            "expense.view", "expense.create", "expense.update", "expense.delete", "expense.approve",
            "report.view", "report.export",
        ]),
        "is_active": True,
    },
    {
        "id": "00000000-0000-4000-a000-000000000005",
        "organization_id": None,
        "name": "Field Employee",
        "slug": "field_employee",
        "description": "Submit expense reports from the field",
        "is_system_role": True,
        "permissions": json.dumps([
            "expense.view",
            "expense.create",
        ]),
        "is_active": True,
    },
]


async def seed_roles(db: AsyncSession) -> None:
    """Insert default system roles if they don't already exist.

    This function is idempotent – running it multiple times has no effect
    once the roles are in the database.

    Args:
        db: Active async database session.
    """
    for role_data in DEFAULT_ROLES:
        stmt = select(Role).where(Role.id == role_data["id"])
        result = await db.execute(stmt)
        if result.scalar_one_or_none() is None:
            db.add(Role(**role_data))
    await db.flush()
