"""
BuildCore FastAPI Dependencies.

Reusable dependency functions for authentication, authorization,
and database session injection.
"""

from typing import Any

from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenError, TenantError, UnauthorizedError
from app.core.middleware import get_tenant_id
from app.core.security import verify_token
from app.database import get_db


# ---------------------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------------------

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

bearer_scheme = HTTPBearer(auto_error=False)

def _extract_bearer_token(authorization: str | None) -> str:
    """Pull the raw token from an Authorization header.

    Args:
        authorization: Full Authorization header value.

    Returns:
        The JWT string without the "Bearer " prefix.

    Raises:
        UnauthorizedError: If header is missing or malformed.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise UnauthorizedError(message="Missing or invalid Authorization header")
    token = authorization.removeprefix("Bearer ").strip()
    if not token:
        raise UnauthorizedError(message="Empty bearer token")
    return token


async def get_current_user(
    token_auth: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    authorization: str | None = Header(default=None),
) -> dict[str, Any]:
    """FastAPI dependency – verify JWT and return payload claims.

    The returned dict contains at minimum:
        - sub: user_id
        - organization_id: tenant UUID
        - email: user email
        - is_super_admin: bool

    Args:
        authorization: Raw Authorization header from the request.

    Returns:
        Decoded JWT payload dict.

    Raises:
        UnauthorizedError: If the token is invalid or expired.
    """
    if token_auth:
        token = token_auth.credentials
    else:
        token = _extract_bearer_token(authorization)
    
    payload = verify_token(token)

    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedError(message="Token missing subject claim")

    return payload


async def require_super_admin(
    current_user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, Any]:
    """FastAPI dependency – ensure the authenticated user is a super admin.

    Args:
        current_user: Decoded JWT payload from get_current_user.

    Returns:
        The same payload dict if authorized.

    Raises:
        ForbiddenError: If is_super_admin is not truthy.
    """
    if not current_user.get("is_super_admin"):
        raise ForbiddenError(message="Super admin access required")
    return current_user


async def require_tenant(
    current_user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, Any]:
    """FastAPI dependency – ensure a valid tenant context exists.

    Checks both the JWT claim and the middleware-set context variable.

    Args:
        current_user: Decoded JWT payload from get_current_user.

    Returns:
        The payload dict if tenant is present.

    Raises:
        TenantError: If no tenant could be resolved.
    """
    # JWT claim
    jwt_org = current_user.get("organization_id")

    # Middleware context
    ctx_org = get_tenant_id()

    tenant = jwt_org or ctx_org
    if not tenant:
        raise TenantError(
            message="No organization context found",
            details={"hint": "Ensure your JWT contains organization_id"},
        )

    return current_user


# ---------------------------------------------------------------------------
# Database session re-export
# ---------------------------------------------------------------------------

async def get_db_session() -> AsyncSession:
    """FastAPI dependency – provide an async database session.

    Delegates to ``app.database.get_db``.
    """
    async for session in get_db():
        yield session
