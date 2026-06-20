"""
FastAPI middleware: attach entitlement context and enforce premium routes.
"""
from __future__ import annotations

import logging
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from backend.entitlements import entitlement_service

logger = logging.getLogger(__name__)

SKIP_PATHS = frozenset(
    {
        "/api/health",
        "/api/status",
        "/api/entitlements",
        "/api/entitlements/activate",
        "/api/entitlements/dev-key",
        "/docs",
        "/openapi.json",
        "/redoc",
        "/",
        "/ws",
    }
)


class EntitlementMiddleware(BaseHTTPMiddleware):
    """Inject plan into request state; block premium API routes in strict mode."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        ctx = entitlement_service.resolve()
        request.state.entitlements = ctx

        path = request.url.path
        if path.startswith("/api/") and path not in SKIP_PATHS:
            allowed, missing = entitlement_service.check_path(path)
            if not allowed and missing:
                return JSONResponse(
                    status_code=403,
                    content={
                        "status": "forbidden",
                        "error": "Feature not available on current plan",
                        "required_feature": missing,
                        "current_plan": ctx.plan.value,
                        "upgrade_url": "https://github.com/ezsoftwarez/Noahubai/blob/main/docs/PRICING.md",
                    },
                )

        response = await call_next(request)
        response.headers["X-Noahubai-Plan"] = ctx.plan.value
        return response
