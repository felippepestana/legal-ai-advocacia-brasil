from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from ai_provider.context import bind_ai_context, reset_ai_context
from services.api.auth import auth_required, is_public_path, resolve_tenant
from services.api.config import API_PREFIX
from services.api.rate_limit import check_rate_limit, resolve_limit


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if is_public_path(request.url.path, API_PREFIX):
            return await call_next(request)

        tenant_id = getattr(request.state, "tenant_id", "public")
        if tenant_id == "public":
            client_host = request.client.host if request.client else "unknown"
            bucket_key = f"ip:{client_host}"
        else:
            bucket_key = f"tenant:{tenant_id}"

        tenant_rpm = getattr(request.state, "rate_limit_rpm", None)
        limit_cfg = resolve_limit(tenant_rpm)
        allowed, retry_after, headers = check_rate_limit(bucket_key, limit_cfg)
        if not allowed:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Limite de requisições excedido. Tente novamente em breve.",
                    "retry_after_seconds": retry_after,
                },
                headers=headers,
            )

        response = await call_next(request)
        for key, value in headers.items():
            response.headers[key] = value
        return response


class TenantAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if is_public_path(request.url.path, API_PREFIX):
            request.state.tenant_id = "public"
            request.state.tenant_name = None
            tokens = bind_ai_context(tenant_id="public")
            try:
                return await call_next(request)
            finally:
                reset_ai_context(tokens)

        tenant = resolve_tenant(request)
        if tenant is None and auth_required():
            return JSONResponse(
                status_code=401,
                content={
                    "detail": "API key ausente ou inválida. Envie X-API-Key ou Authorization: Bearer.",
                },
            )

        request.state.tenant_id = tenant.tenant_id if tenant else "public"
        request.state.tenant_name = tenant.name if tenant else None
        request.state.rate_limit_rpm = tenant.rate_limit_rpm if tenant else None

        tokens = bind_ai_context(tenant_id=request.state.tenant_id)
        try:
            return await call_next(request)
        finally:
            reset_ai_context(tokens)
