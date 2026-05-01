"""
Role Pydantic schemas with permission key enum validation.
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class PermissionKey(str, Enum):
    """All available permission keys for RBAC.

    These are validated in Pydantic but stored as plain strings in the DB.
    New permissions can be added here as features are implemented.
    """

    # User management
    USER_VIEW = "user.view"
    USER_CREATE = "user.create"
    USER_UPDATE = "user.update"
    USER_DELETE = "user.delete"
    USER_INVITE = "user.invite"

    # Role management
    ROLE_VIEW = "role.view"
    ROLE_CREATE = "role.create"
    ROLE_UPDATE = "role.update"
    ROLE_DELETE = "role.delete"

    # Organization management
    ORG_VIEW = "org.view"
    ORG_UPDATE = "org.update"

    # Project management
    PROJECT_VIEW = "project.view"
    PROJECT_CREATE = "project.create"
    PROJECT_UPDATE = "project.update"
    PROJECT_DELETE = "project.delete"

    # Employee management
    EMPLOYEE_VIEW = "employee.view"
    EMPLOYEE_CREATE = "employee.create"
    EMPLOYEE_UPDATE = "employee.update"
    EMPLOYEE_DELETE = "employee.delete"

    # Contractor management
    CONTRACTOR_VIEW = "contractor.view"
    CONTRACTOR_CREATE = "contractor.create"
    CONTRACTOR_UPDATE = "contractor.update"
    CONTRACTOR_DELETE = "contractor.delete"

    # Expense management
    EXPENSE_VIEW = "expense.view"
    EXPENSE_CREATE = "expense.create"
    EXPENSE_UPDATE = "expense.update"
    EXPENSE_DELETE = "expense.delete"
    EXPENSE_APPROVE = "expense.approve"

    # Reports
    REPORT_VIEW = "report.view"
    REPORT_EXPORT = "report.export"

    # Audit
    AUDIT_VIEW = "audit.view"

    # Settings
    SETTINGS_VIEW = "settings.view"
    SETTINGS_UPDATE = "settings.update"

    # Subscription
    SUBSCRIPTION_VIEW = "subscription.view"
    SUBSCRIPTION_UPDATE = "subscription.update"


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------


class RoleCreate(BaseModel):
    """Payload for creating a new role."""

    name: str = Field(..., min_length=1, max_length=100)
    slug: str = Field(..., min_length=1, max_length=100, pattern=r"^[a-z0-9_]+$")
    description: str = Field("", max_length=500)
    permissions: list[str] = Field(default_factory=list)


class RoleUpdate(BaseModel):
    """Payload for updating a role (all fields optional)."""

    name: str | None = Field(None, min_length=1, max_length=100)
    slug: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
    permissions: list[str] | None = None
    is_active: bool | None = None


class PermissionOverrideCreate(BaseModel):
    """Payload for creating a user permission override."""

    user_id: str = Field(..., description="Target user ID")
    permission_key: str = Field(..., description="Permission key to override")
    is_granted: bool = Field(..., description="True to grant, False to revoke")
    reason: str = Field("", max_length=500)
    expires_at: datetime | None = None


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------


class RoleResponse(BaseModel):
    """Role data returned by the API."""

    id: str
    organization_id: str | None = None
    name: str
    slug: str
    description: str | None = None
    is_system_role: bool = False
    permissions: list[str] = Field(default_factory=list)
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PermissionOverrideResponse(BaseModel):
    """Permission override data returned by the API."""

    id: str
    user_id: str
    permission_key: str
    is_granted: bool
    granted_by: str | None = None
    reason: str | None = None
    expires_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
