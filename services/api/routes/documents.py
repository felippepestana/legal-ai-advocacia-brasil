from fastapi import APIRouter, HTTPException

from legal_core.serializers import validation_to_api_payload
from legal_core.validators import validate_peticao_inicial
from services.api.adapters import documents as documents_adapter
from services.api.schemas import AnalyzeDocumentRequest, ValidateDocumentRequest

router = APIRouter()


@router.post("/analyze")
def analyze_document(body: AnalyzeDocumentRequest) -> dict:
    try:
        return documents_adapter.analyze_document_text(
            body.text,
            body.legal_area,
            body.enhance_with_gemini,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/validate")
def validate_document(body: ValidateDocumentRequest) -> dict:
    if body.tipo_peca == "peticao_inicial":
        result = validate_peticao_inicial(body.text, tipo_peca=body.tipo_peca)
        return validation_to_api_payload(result)
    raise HTTPException(
        status_code=400,
        detail=f"Validador não implementado para tipo: {body.tipo_peca}",
    )
