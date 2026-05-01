"""
BuildCore Application Entry Point.

Creates the FastAPI application, registers middleware, exception handlers,
and all route modules.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.core.exceptions import BuildCoreError
from app.core.middleware import TenantMiddleware
from app.core.responses import error_response

settings = get_settings()

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)

# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(TenantMiddleware)

# ---------------------------------------------------------------------------
# Exception handlers
# ---------------------------------------------------------------------------


@app.exception_handler(BuildCoreError)
async def buildcore_exception_handler(request: Request, exc: BuildCoreError):
    """Catch all BuildCoreError subclasses and return a standard error envelope."""
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(exc),
    )

# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------


@app.get("/")
async def health_check():
    """Liveness probe – confirms the API is running."""
    return {"status": "ok", "service": settings.APP_NAME}

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

from app.routes.auth import router as auth_router
from app.routes.organizations import router as org_router
from app.routes.users import router as user_router
from app.routes.roles import router as role_router
from app.routes.sdui import router as sdui_router
from app.routes.subscriptions import router as sub_router
from app.routes.audit_logs import router as audit_router

app.include_router(auth_router, prefix=settings.API_PREFIX)
app.include_router(org_router, prefix=settings.API_PREFIX)
app.include_router(user_router, prefix=settings.API_PREFIX)
app.include_router(role_router, prefix=settings.API_PREFIX)
app.include_router(sdui_router, prefix=settings.API_PREFIX)
app.include_router(sub_router, prefix=settings.API_PREFIX)
app.include_router(audit_router, prefix=settings.API_PREFIX)
