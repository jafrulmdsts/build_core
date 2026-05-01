from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer

from app.models.base import BaseModel


class Organization(BaseModel):
    """Multi-tenant organization entity (construction company / builder firm)."""

    __tablename__ = "organizations"

    name = Column(String(200), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    logo_url = Column(String(500), nullable=True)
    address = Column(Text, nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    website = Column(String(500), nullable=True)
    reg_number = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    subscription_plan_id = Column(String(36), nullable=True)
    subscription_start_date = Column(DateTime(timezone=True), nullable=True)
    subscription_end_date = Column(DateTime(timezone=True), nullable=True)
    max_users = Column(Integer, nullable=True)
    max_projects = Column(Integer, nullable=True)
    currency_code = Column(String(3), default="BDT")
    timezone = Column(String(50), default="Asia/Dhaka")
    settings = Column(Text, nullable=True)
