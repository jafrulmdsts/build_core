from sqlalchemy import Column, String, Boolean, Text

from app.models.base import BaseModel


class Role(BaseModel):
    """Role entity — organization-scoped or system-level roles."""

    __tablename__ = "roles"

    organization_id = Column(String(36), nullable=True)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    is_system_role = Column(Boolean, default=False)
    permissions = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
