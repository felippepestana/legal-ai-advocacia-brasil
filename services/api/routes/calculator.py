from fastapi import APIRouter, HTTPException

from services.api.adapters import calculator as calculator_adapter
from services.api.schemas import CalculateLegalRequest

router = APIRouter()


@router.post("/run")
def run_calculation(body: CalculateLegalRequest) -> dict:
    try:
        return calculator_adapter.run_calculation(
            body.area, body.subtype, body.parameters
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
