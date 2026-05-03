"""
BuildCore Application Entry Point.

Creates the FastAPI application, registers middleware, exception handlers,
and all route modules.
"""

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.config import get_settings
from app.core.exceptions import BuildCoreError
from app.core.middleware import TenantMiddleware
from app.core.responses import error_response

logger = logging.getLogger("buildcore")

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


@app.exception_handler(RequestValidationError)
async def request_validation_handler(request: Request, exc: RequestValidationError):
    """Catch FastAPI request-body / query-parameter validation errors."""
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Validation failed",
                "details": [
                    {"field": err["loc"][-1], "message": err["msg"]}
                    for err in exc.errors()
                ],
            },
        },
    )


@app.exception_handler(ValidationError)
async def pydantic_validation_handler(request: Request, exc: ValidationError):
    """Catch Pydantic model_validate / schema-level validation errors."""
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Validation failed",
                "details": [
                    {"field": err["loc"][-1], "message": err["msg"]}
                    for err in exc.errors()
                ],
            },
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Catch-all for any unhandled exceptions — prevents raw 500s leaking."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "details": [],
            },
        },
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
from app.routes.locations import router as location_router
from app.routes.employees import router as employee_router
from app.routes.contractors import router as contractor_router
from app.routes.projects import router as project_router
from app.routes.expenses import router as expense_router
from app.routes.files import router as files_router
from app.routes.currencies import router as currency_router

app.include_router(auth_router, prefix=settings.API_PREFIX)
app.include_router(org_router, prefix=settings.API_PREFIX)
app.include_router(user_router, prefix=settings.API_PREFIX)
app.include_router(role_router, prefix=settings.API_PREFIX)
app.include_router(sdui_router, prefix=settings.API_PREFIX)
app.include_router(sub_router, prefix=settings.API_PREFIX)
app.include_router(audit_router, prefix=settings.API_PREFIX)
app.include_router(location_router, prefix=settings.API_PREFIX)
app.include_router(employee_router, prefix=settings.API_PREFIX)
app.include_router(contractor_router, prefix=settings.API_PREFIX)
app.include_router(project_router, prefix=settings.API_PREFIX)
app.include_router(expense_router, prefix=settings.API_PREFIX)
app.include_router(files_router, prefix=settings.API_PREFIX)
app.include_router(currency_router, prefix=settings.API_PREFIX)
