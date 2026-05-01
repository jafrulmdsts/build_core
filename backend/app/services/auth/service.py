"""
Auth service — business logic for authentication flows.

Handles login, invite-based registration, token refresh, user invitation,
and logout. All errors follow fail-fast semantics with BuildCoreError
subclasses raised on the first validation failure.
"""

from datetime import datetime, timezone, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core.exceptions import (
    ConflictError,
    NotFoundError,
    UnauthorizedError,
    ValidationError,
)
from app.core.security import (
    create_access_token,
    create_refresh_token,
    generate_invite_token,
    get_password_hash,
    verify_password,
    verify_token,
)
from app.models.role import Role
from app.models.user import User
from app.services.auth.crud import (
    create_user,
    get_user_by_email,
    get_user_by_id,
    get_user_by_invite_token,
    update_user,
)

_settings = get_settings()


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _build_token_claims(user: User) -> dict:
    """Build the standard JWT payload for a user.

    Args:
        user: Authenticated User instance.

    Returns:
        Dict with sub, email, organization_id, role_id, is_super_admin.
    """
    return {
        "sub": user.id,
        "email": user.email,
        "organization_id": user.organization_id,
        "role_id": user.role_id,
        "is_super_admin": user.is_super_admin,
    }


def _build_token_response(user: User) -> dict:
    """Create JWT token pair and build the full login response dict.

    Args:
        user: Authenticated User instance.

    Returns:
        Dict matching LoginResponse schema.
    """
    claims = _build_token_claims(user)

    access_token = create_access_token(claims)
    refresh_token_str = create_refresh_token(claims)

    return {
        "token": {
            "access_token": access_token,
            "refresh_token": refresh_token_str,
            "token_type": "Bearer",
            "expires_in": _settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        },
        "user_id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "is_super_admin": user.is_super_admin,
        "organization_id": user.organization_id,
        "role_id": user.role_id,
    }


# ---------------------------------------------------------------------------
# Public service functions
# ---------------------------------------------------------------------------


async def login(
    db: AsyncSession,
    email: str,
    password: str,
    ip_address: str | None = None,
) -> dict:
    """Authenticate a user with email and password.

    Args:
        db: Async database session.
        email: User email address.
        password: Plaintext password.
        ip_address: Optional caller IP (for future audit logging).

    Returns:
        Dict matching LoginResponse schema with token pair + user info.

    Raises:
        UnauthorizedError: If user not found, inactive, or password wrong.
    """
    # 1. Look up user by email
    user = await get_user_by_email(db, email)
    if user is None:
        raise UnauthorizedError(message="Invalid email or password")

    # 2. Check account is active
    if not user.is_active:
        raise UnauthorizedError(message="Account is deactivated")

    # 3. Verify password
    if not verify_password(password, user.password_hash):
        raise UnauthorizedError(message="Invalid email or password")

    # 4. Update last_login_at
    await update_user(db, user.id, last_login_at=datetime.now(timezone.utc))

    # 5 & 6. Build and return token response
    return _build_token_response(user)


async def register(
    db: AsyncSession,
    token: str,
    first_name: str,
    last_name: str,
    password: str,
    phone: str,
) -> dict:
    """Complete registration via an invite token.

    The user record is pre-created by ``invite_user`` with
    ``is_active=False`` and a valid invite token.  This endpoint
    verifies the token, sets the password, and activates the account.

    Args:
        db: Async database session.
        token: Invite token from the email link.
        first_name: New user's first name.
        last_name: New user's last name.
        password: Chosen plaintext password.
        phone: Phone number.

    Returns:
        Dict matching LoginResponse schema — user can immediately authenticate.

    Raises:
        NotFoundError: If no user matches the invite token.
        ValidationError: If the invite token has expired.
    """
    now = datetime.now(timezone.utc)

    # 1. Look up user by invite token
    user = await get_user_by_invite_token(db, token)
    if user is None:
        raise NotFoundError(message="Invalid invite token")

    # 2. Check token expiry
    if user.invite_token_expires_at is not None and user.invite_token_expires_at <= now:
        raise ValidationError(
            message="Invite token has expired",
            details={"invite_token_expires_at": user.invite_token_expires_at.isoformat()},
        )

    # 3. Hash password
    password_hash = get_password_hash(password)

    # 4. Activate user — clear invite fields, set verified timestamp
    user = await update_user(
        db,
        user.id,
        password_hash=password_hash,
        first_name=first_name,
        last_name=last_name,
        phone=phone,
        invite_token=None,
        invite_token_expires_at=None,
        email_verified_at=now,
        is_active=True,
        last_login_at=now,
    )

    # 5 & 6. Build and return token response
    return _build_token_response(user)


async def refresh_token(db: AsyncSession, refresh_token_str: str) -> dict:
    """Exchange a valid refresh token for a new access token.

    Args:
        db: Async database session.
        refresh_token_str: Encoded JWT refresh token.

    Returns:
        TokenData dict with new access_token and the same refresh_token.

    Raises:
        UnauthorizedError: If token is invalid or not a refresh token.
        NotFoundError: If the user referenced by the token no longer exists.
    """
    # 1. Decode and verify the JWT
    payload = verify_token(refresh_token_str)

    # 2. Ensure it is a refresh-type token
    if payload.get("type") != "refresh":
        raise UnauthorizedError(message="Invalid token type")

    # 3. Resolve the user
    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedError(message="Token missing subject claim")

    user = await get_user_by_id(db, user_id)
    if user is None:
        raise NotFoundError(message="User not found")

    # 4. Ensure user is still active
    if not user.is_active:
        raise UnauthorizedError(message="Account is deactivated")

    # 5. Issue a new access token with the same claims
    claims = _build_token_claims(user)
    new_access_token = create_access_token(claims)

    # 6. Return TokenData
    return {
        "access_token": new_access_token,
        "refresh_token": refresh_token_str,
        "token_type": "Bearer",
        "expires_in": _settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }


async def invite_user(
    db: AsyncSession,
    organization_id: str,
    invited_by: str,
    email: str,
    first_name: str,
    last_name: str,
    role_id: str,
    phone: str,
) -> User:
    """Invite a new user to an organization.

    Creates an inactive user record with an invite token.  The invited
    person completes registration via ``register()``.

    Args:
        db: Async database session.
        organization_id: Org that owns the invitation.
        invited_by: User ID of the inviter.
        email: Email of the person to invite.
        first_name: Invitee's first name.
        last_name: Invitee's last name.
        role_id: Role to assign in the organization.
        phone: Invitee's phone number.

    Returns:
        The newly created (inactive) User instance.

    Raises:
        ConflictError: If the email is already registered.
        NotFoundError: If the role_id does not exist for the org or as a system role.
    """
    # 1. Check email uniqueness
    existing = await get_user_by_email(db, email)
    if existing is not None:
        raise ConflictError(
            message="A user with this email already exists",
            details={"email": email},
        )

    # 2. Validate role — must belong to the same org or be a system role
    role_stmt = select(Role).where(
        Role.id == role_id,
        Role.deleted_at.is_(None),
        Role.is_active.is_(True),
        # Either org-scoped for this org OR a global system role
        (Role.organization_id == organization_id) | (Role.is_system_role.is_(True)),  # type: ignore[operator]
    )
    role_result = await db.execute(role_stmt)
    if role_result.scalar_one_or_none() is None:
        raise NotFoundError(
            message="Role not found for this organization",
            details={"role_id": role_id, "organization_id": organization_id},
        )

    # 3. Generate invite token
    token = generate_invite_token()

    # 4. Set expiry (7 days from now)
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(days=7)

    # 5. Create user (inactive until they complete registration)
    user = await create_user(
        db,
        organization_id=organization_id,
        email=email,
        password_hash="$argon2id$placeholder",  # replaced during registration
        first_name=first_name,
        last_name=last_name,
        phone=phone,
        role_id=role_id,
        is_active=False,
        invite_token=token,
        invite_token_expires_at=expires_at,
        invited_by=invited_by,
    )

    # 6. Return the created user
    return user


async def logout(db: AsyncSession, user_id: str) -> None:
    """Logout — currently a placeholder.

    The client is expected to discard tokens.  Future iterations
    may add a token blacklist for server-side revocation.

    Args:
        db: Async database session.
        user_id: ID of the user logging out.
    """
    # Placeholder — client discards tokens.
    # Future: add token to blacklist store (Redis, DB table, etc.)
    pass
