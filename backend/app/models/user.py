from sqlalchemy import Column, String, DateTime, Boolean, Text

from app.models.base import BaseModel


class User(BaseModel):
    """User entity — may belong to an organization or be a Super Admin."""

    __tablename__ = "users"

    organization_id = Column(String(36), nullable=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    role_id = Column(String(36), nullable=True)
    is_active = Column(Boolean, default=True)
    email_verified_at = Column(DateTime(timezone=True), nullable=True)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    is_super_admin = Column(Boolean, default=False)
    invite_token = Column(String(255), nullable=True, unique=True)
    invite_token_expires_at = Column(DateTime(timezone=True), nullable=True)
    invited_by = Column(String(36), nullable=True)
    language_preference = Column(String(5), default="bn")
    settings = Column(Text, nullable=True)
