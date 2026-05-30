from fastapi import APIRouter, HTTPException, Request

from services.api.adapters import search as search_adapter
from services.api.schemas import SearchRequest

router = APIRouter()


@router.post("/query")
def search_legal(body: SearchRequest, request: Request) -> dict:
    tenant_id = getattr(request.state, "tenant_id", "public")
    try:
        return search_adapter.run_search(
            body.query,
            body.search_type,
            body.filters,
            body.synthesize_with_gemini,
            body.use_external_sources,
            body.tribunals or None,
            user_id=tenant_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc