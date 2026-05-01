"""
BuildCore Tenant Middleware.

ASGI middleware that extracts the tenant (organization) ID from the
JWT access token (or X-Organization-ID header) and stores it in a
context variable for the lifetime of the request.

Public paths (auth, health, docs) are skipped so tenant resolution
is not required for login / registration / token refresh.
"""

from contextvars import ContextVar
from typing import Any, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.exceptions import UnauthorizedError
from app.core.security import verify_token

# ---------------------------------------------------------------------------
# Context variable – set once per request by TenantMiddleware
# ---------------------------------------------------------------------------

_tenant_id: ContextVar[str | None] = ContextVar("tenant_id", default=None)


def get_tenant_id() -> str | None:
    """Return the current request's tenant (organization) ID.

    Returns:
        The tenant UUID string, or None if not set (public routes).
    """
    return _tenant_id.get()


def set_tenant_id(tenant_id: str | None) -> None:
    """Store the tenant ID for the current request context.

    Args:
        tenant_id: Organization UUID or None to clear.
    """
    _tenant_id.set(tenant_id)


# ---------------------------------------------------------------------------
# Paths that do NOT require tenant resolution
# ---------------------------------------------------------------------------

_PUBLIC_PATH_PREFIXES: tuple[str, ...] = (
    "/api/v1/auth/",
    "/health",
    "/docs",
    "/openapi.json",
    "/redoc",
)

_ROOT_PATHS: tuple[str, ...] = ("/",)


class TenantMiddleware(BaseHTTPMiddleware):
    """Extract organization_id from JWT and store in context.

    Resolution strategy:
    1. Decode Authorization: Bearer <token> → read "organization_id" claim.
    2. Fall back to X-Organization-ID header (dev convenience).
    3. Public paths are skipped entirely (tenant_id remains None).
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        path: str = request.url.path

        # Skip tenant resolution for public routes
        if self._is_public_path(path):
            return await call_next(request)

        # Strategy 1 – JWT
        tenant = self._extract_from_jwt(request)

        # Strategy 2 – header fallback
        if tenant is None:
            tenant = request.headers.get("X-Organization-ID")

        set_tenant_id(tenant)
        try:
            response: Response = await call_next(request)
        finally:
            # Clear context after response to avoid leaking across requests
            _tenant_id.set(None)
        return response

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _is_public_path(path: str) -> bool:
        """Return True if the path should skip tenant resolution."""
        if path in _ROOT_PATHS:
            return True
        return any(path.startswith(prefix) for prefix in _PUBLIC_PATH_PREFIXES)

    @staticmethod
    def _extract_from_jwt(request: Request) -> str | None:
        """Decode the JWT from the Authorization header and return organization_id.

        Returns None if no token is present or the claim is missing.
        Does NOT raise – that is handled by dependency checks later.
        """
        auth_header: str | None = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None

        token = auth_header.removeprefix("Bearer ").strip()
        if not token:
            return None

        try:
            payload: dict[str, Any] = verify_token(token)
        except UnauthorizedError:
            return None

        return payload.get("organization_id")
