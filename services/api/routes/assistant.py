from fastapi import APIRouter, HTTPException, Request

from services.api.adapters import assistant as assistant_adapter
from services.api.schemas import AssistantChatRequest

router = APIRouter()


@router.post("/chat")
def assistant_chat(body: AssistantChatRequest, request: Request) -> dict:
    tenant_id = getattr(request.state, "tenant_id", "public")
    try:
        return assistant_adapter.chat(
            body.message,
            body.user_level,
            user_id=tenant_id,
            enhance_with_gemini=body.enhance_with_gemini,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc