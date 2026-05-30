from datetime import datetime, timezone

from fastapi import APIRouter, Request
from fastapi.responses import Response

from legal_core import HUB_ROOT
from legal_core.ontology import document_type_ids, legal_area_ids
from legal_core.prompts import list_prompts
from services.api.schemas import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    from ai_provider.gemini import get_ai_status, is_gemini_available
    from services.api.auth import auth_status
    from services.api.alerts import slack_alerts_enabled
    from services.api.observability import monitoring_status
    from services.api.rate_limit import rate_limit_status
    from legal_sources.cache import cache_status
    from infra.redis import redis_status

    ai = get_ai_status()
    auth = auth_status()
    rate = rate_limit_status()
    monitoring = monitoring_status()
    cache = cache_status()
    redis = redis_status()
    return HealthResponse(
        status="ok",
        version="0.1.0",
        hub=str(HUB_ROOT.name),
        gemini_available=is_gemini_available(),
        ai_backend=ai.get("backend"),
        ai_model=ai.get("model"),
        ai_project=ai.get("project"),
        ai_location=ai.get("location"),
        auth_required=auth["required"],
        tenants_configured=auth["tenants_configured"],
        rate_limit_enabled=rate["enabled"],
        rate_limit_requests=rate["max_requests"],
        rate_limit_window_seconds=rate["window_seconds"],
        rate_limit_backend=rate.get("backend"),
        search_cache_backend=cache.get("backend"),
        sentry_enabled=monitoring.get("sentry_enabled", False),
        structured_logging=monitoring.get("structured_logging", False),
        slack_alerts_enabled=slack_alerts_enabled(),
        redis_enabled=redis["enabled"],
        redis_connected=redis["connected"],
    )


@router.get("/audit/recent")
def audit_recent(request: Request, limit: int = 20) -> dict:
    from services.api.audit_store import read_events_for_tenant

    tenant_id = getattr(request.state, "tenant_id", "public")
    events = read_events_for_tenant(tenant_id, limit=limit)
    return {"tenant_id": tenant_id, "events": events, "count": len(events)}


@router.get("/audit/export")
def audit_export_csv(request: Request, limit: int = 500) -> Response:
    from services.api.audit_store import events_to_csv, read_events_for_tenant

    tenant_id = getattr(request.state, "tenant_id", "public")
    safe_limit = max(1, min(limit, 5000))
    events = read_events_for_tenant(tenant_id, limit=safe_limit)
    csv_body = events_to_csv(events)
    day = datetime.now(timezone.utc).strftime("%Y%m%d")
    filename = f"auditoria_ia_{tenant_id}_{day}.csv"
    return Response(
        content=csv_body,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/ontology/document-types")
def ontology_document_types() -> dict:
    return {"tipos": document_type_ids()}


@router.get("/ontology/legal-areas")
def ontology_legal_areas() -> dict:
    return {"areas": legal_area_ids()}


@router.get("/prompts")
def prompts_index() -> dict:
    return {"prompts": list_prompts()}


@router.get("/prompts/{name}")
def prompts_get(name: str) -> dict:
    from legal_core.prompts import load_prompt

    return {"name": name, "content": load_prompt(name)}
