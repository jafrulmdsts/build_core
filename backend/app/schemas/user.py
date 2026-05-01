"""
User Pydantic schemas (request/response).
"""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserUpdate(BaseModel):
    """Payload for updating user profile (all fields optional)."""

    first_name: str | None = Field(None, min_length=1, max_length=100)
    last_name: str | None = Field(None, max_length=100)
    phone: str | None = Field(None, max_length=20)
    avatar_url: str | None = Field(None, max_length=500)
    language_preference: str | None = Field(None, max_length=5)
    role_id: str | None = None
    is_active: bool | None = None


class UserResponse(BaseModel):
    """User data returned by the API."""

    id: str
    organization_id: str | None = None
    email: str
    first_name: str
    last_name: str | None = None
    phone: str | None = None
    avatar_url: str | None = None
    role_id: str | None = None
    is_active: bool = True
    email_verified_at: datetime | None = None
    last_login_at: datetime | None = None
    is_super_admin: bool = False
    language_preference: str = "bn"
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class InviteListResponse(BaseModel):
    """Summary of a pending or used invitation."""

    id: str
    email: str
    first_name: str
    last_name: str | None = None
    role_id: str | None = None
    invited_by: str | None = None
    invite_token: str | None = None
    invite_token_expires_at: datetime | None = None
    is_active: bool
    email_verified_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
