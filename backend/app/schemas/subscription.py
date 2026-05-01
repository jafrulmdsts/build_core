"""
Subscription plan Pydantic schema (read-only for now).
"""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


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
