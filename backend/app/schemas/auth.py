"""
Auth-related Pydantic schemas for login, registration, and token management.

Uses Python enums for validation (no DB ENUMs).
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, EmailStr, Field


class UserStatus(str, Enum):
    """User account status values (validated in Pydantic, stored as String in DB)."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------


class LoginRequest(BaseModel):
    """Payload for user login."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=6, description="User password")


class RegisterRequest(BaseModel):
    """Payload for invite-based user registration."""

    token: str = Field(..., description="Invite token from email link")
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field("", max_length=100)
    password: str = Field(..., min_length=8, max_length=128)
    phone: str = Field("", max_length=20)


class InviteUserRequest(BaseModel):
    """Payload for inviting a new user to an organization."""

    email: EmailStr = Field(..., description="Email of the person to invite")
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field("", max_length=100)
    role_id: str = Field(..., description="Role ID to assign")
    phone: str = Field("", max_length=20)


class ChangePasswordRequest(BaseModel):
    """Payload for changing a user's password."""

    current_password: str = Field(..., min_length=6, description="Current password")
    new_password: str = Field(..., min_length=8, max_length=128, description="New password")


class RefreshTokenRequest(BaseModel):
    """Payload for refreshing an access token."""

    refresh_token: str = Field(..., description="Valid refresh token")


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------


class TokenData(BaseModel):
    """JWT token pair returned after login or registration."""

    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int = Field(..., description="Access token expiry in seconds")


class LoginResponse(BaseModel):
    """Response payload for successful login."""

    token: TokenData
    user_id: str
    email: str
    first_name: str
    last_name: str | None = None
    is_super_admin: bool = False
    organization_id: str | None = None
    role_id: str | None = None
