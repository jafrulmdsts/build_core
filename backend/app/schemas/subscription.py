"""
Subscription plan Pydantic schemas for CRUD operations.
"""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class SubscriptionPlanCreate(BaseModel):
    """Schema for creating a new subscription plan."""

    name: str = Field(..., min_length=1, max_length=50)
    slug: str = Field(..., min_length=1, max_length=50, pattern=r"^[a-z0-9-]+$")
    description: str | None = None
    price_monthly: Decimal = Field(default=Decimal("0"), ge=0)
    price_yearly: Decimal = Field(default=Decimal("0"), ge=0)
    max_users: int | None = Field(default=None, ge=0)
    max_projects: int | None = Field(default=None, ge=0)
    max_storage_mb: int | None = Field(default=None, ge=0)
    features: list[str] = Field(default_factory=list)
    trial_days: int | None = Field(default=None, ge=0)
    is_active: bool = True


class SubscriptionPlanUpdate(BaseModel):
    """Schema for updating an existing subscription plan."""

    name: str | None = Field(default=None, min_length=1, max_length=50)
    slug: str | None = Field(default=None, min_length=1, max_length=50, pattern=r"^[a-z0-9-]+$")
    description: str | None = None
    price_monthly: Decimal | None = Field(default=None, ge=0)
    price_yearly: Decimal | None = Field(default=None, ge=0)
    max_users: int | None = Field(default=None, ge=0)
    max_projects: int | None = Field(default=None, ge=0)
    max_storage_mb: int | None = Field(default=None, ge=0)
    features: list[str] | None = None
    trial_days: int | None = Field(default=None, ge=0)
    is_active: bool | None = None


class SubscriptionPlanResponse(BaseModel):
    """Subscription plan data returned by the API."""

    id: str
    name: str
    slug: str
    description: str | None = None
    price_monthly: Decimal = Decimal("0")
    price_yearly: Decimal = Decimal("0")
    max_users: int | None = None
    max_projects: int | None = None
    max_storage_mb: int | None = None
    features: list[str] = Field(default_factory=list)
    trial_days: int | None = None
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
