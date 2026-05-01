"""
BuildCore Authentication Routes.

Public endpoints for login, registration, token refresh, invite, and logout.
"""

from fastapi import APIRouter, Depends, Request

from app.core.exceptions import BuildCoreError
from app.core.responses import error_response, success_response
from app.core.dependencies import get_current_user, require_tenant, get_db_session
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    InviteUserRequest,
    RefreshTokenRequest,
    ChangePasswordRequest,
)
from app.services.auth.service import login, register, refresh_token, invite_user, logout, change_password

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login")
async def login_endpoint(
    body: LoginRequest,
    request: Request,
    db=Depends(get_db_session),
):
    """Authenticate user with email and password.

    Returns JWT access/refresh token pair and user profile data.
    """
    try:
        client_ip = request.client.host if request.client else "unknown"
        data = await login(db, body.email, body.password, client_ip)
        return success_response(data=data, message="Login successful")
    except BuildCoreError as exc:
        return error_response(exc)


@router.post("/register")
async def register_endpoint(
    body: RegisterRequest,
    request: Request,
    db=Depends(get_db_session),
):
    """Complete invite-based registration.

    Accepts an invite token along with new user profile details.
    """
    try:
        data = await register(
            db,
            token=body.token,
            first_name=body.first_name,
            last_name=body.last_name,
            password=body.password,
            phone=body.phone,
        )
        return success_response(data=data, message="Registration successful")
    except BuildCoreError as exc:
        return error_response(exc)


@router.post("/refresh")
async def refresh_endpoint(
    body: RefreshTokenRequest,
    db=Depends(get_db_session),
):
    """Exchange a valid refresh token for a new access token."""
    try:
        data = await refresh_token(db, body.refresh_token)
        return success_response(data=data, message="Token refreshed")
    except BuildCoreError as exc:
        return error_response(exc)


@router.post("/invite")
async def invite_endpoint(
    body: InviteUserRequest,
    request: Request,
    db=Depends(get_db_session),
    current_user: dict = Depends(require_tenant),
):
    """Invite a new user to the authenticated organization.

    Requires an active tenant context and valid JWT.
    """
    try:
        org_id = current_user.get("organization_id")
        inviter_id = current_user.get("sub")
        user = await invite_user(
            db,
            organization_id=org_id,
            invited_by=inviter_id,
            email=body.email,
            first_name=body.first_name,
            last_name=body.last_name,
            role_id=body.role_id,
            phone=body.phone,
        )
        return success_response(
            data={"id": user.id, "email": user.email, "invite_token": user.invite_token},
            message="User invited successfully",
        )
    except BuildCoreError as exc:
        return error_response(exc)


@router.post("/logout")
async def logout_endpoint(
    request: Request,
    db=Depends(get_db_session),
    current_user: dict = Depends(get_current_user),
):
    """Invalidate the current user's active tokens.

    Requires a valid JWT. Client discards tokens.
    """
    try:
        await logout(db, current_user.get("sub"))
        return success_response(message="Logged out successfully")
    except BuildCoreError as exc:
        return error_response(exc)


@router.post("/change-password")
async def change_password_endpoint(
    body: ChangePasswordRequest,
    db=Depends(get_db_session),
    current_user: dict = Depends(get_current_user),
):
    """Change the authenticated user's password.

    Requires current password verification.
    """
    try:
        await change_password(
            db,
            user_id=current_user.get("sub"),
            current_password=body.current_password,
            new_password=body.new_password,
        )
        return success_response(message="Password changed successfully")
    except BuildCoreError as exc:
        return error_response(exc)
