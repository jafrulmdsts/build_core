"""
Organization Pydantic schemas (request/response).

All fields use camelCase for API; snake_case mapping handled at service layer.
"""

from datetime import date, datetime

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------


class OrganizationCreate(BaseModel):
    """Payload for creating a new organization."""

    name: str = Field(..., min_length=1, max_length=200)
    slug: str = Field(..., min_length=1, max_length=100, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    address: str = Field("", max_length=500)
    phone: str = Field("", max_length=20)
    email: str = Field("", max_length=255)
    website: str = Field("", max_length=500)
    reg_number: str = Field("", max_length=100)
    currency_code: str = Field("BDT", max_length=3)
    timezone: str = Field("Asia/Dhaka", max_length=50)
    subscription_plan_id: str | None = Field(None, description="Subscription plan to assign")


class OrganizationUpdate(BaseModel):
    """Payload for updating an existing organization (all fields optional)."""

    name: str | None = Field(None, min_length=1, max_length=200)
    slug: str | None = Field(None, min_length=1, max_length=100)
    logo_url: str | None = Field(None, max_length=500)
    address: str | None = Field(None, max_length=500)
    phone: str | None = Field(None, max_length=20)
    email: str | None = Field(None, max_length=255)
    website: str | None = Field(None, max_length=500)
    reg_number: str | None = Field(None, max_length=100)
    is_active: bool | None = None
    currency_code: str | None = Field(None, max_length=3)
    timezone: str | None = Field(None, max_length=50)
    subscription_plan_id: str | None = None


# ---------------------------------------------------------------------------
# Response schema
# ---------------------------------------------------------------------------


class OrganizationResponse(BaseModel):
    """Organization data returned by the API."""

    id: str
    name: str
    slug: str
    logo_url: str | None = None
    address: str | None = None
    phone: str | None = None
    email: str | None = None
    website: str | None = None
    reg_number: str | None = None
    is_active: bool = True
    subscription_plan_id: str | None = None
    subscription_start_date: date | None = None
    subscription_end_date: date | None = None
    max_users: int | None = None
    max_projects: int | None = None
    currency_code: str = "BDT"
    timezone: str = "Asia/Dhaka"
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
