from sqlalchemy import Column, String, Boolean, Text, Numeric, Integer

from app.models.base import BaseModel


class SubscriptionPlan(BaseModel):
    """Subscription plans available to organizations (Trial, Basic, Premium)."""

    __tablename__ = "subscription_plans"

    name = Column(String(50), nullable=False)
    slug = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    price_monthly = Column(Numeric(10, 2), default=0)
    price_yearly = Column(Numeric(10, 2), default=0)
    max_users = Column(Integer, nullable=True)
    max_projects = Column(Integer, nullable=True)
    max_storage_mb = Column(Integer, nullable=True)
    features = Column(Text, nullable=True)
    trial_days = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)
