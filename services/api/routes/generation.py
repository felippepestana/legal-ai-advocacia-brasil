from fastapi import APIRouter, HTTPException

from services.api.adapters import generation as generation_adapter
from services.api.schemas import GenerateDocumentRequest

router = APIRouter()


@router.get("/templates")
def list_templates() -> dict:
    return {"templates": generation_adapter.list_templates()}


@router.post("/generate")
def generate_document(body: GenerateDocumentRequest) -> dict:
    try:
        return generation_adapter.generate_document(
            body.template_id,
            body.data,
            body.ai_enhancement,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
