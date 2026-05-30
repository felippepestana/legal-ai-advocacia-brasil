from fastapi import APIRouter, HTTPException

from services.api.adapters import deadlines as deadlines_adapter
from services.api.schemas import CalculateDeadlineRequest

router = APIRouter()


@router.post("/calculate")
def calculate_deadline(body: CalculateDeadlineRequest) -> dict:
    try:
        return deadlines_adapter.calculate_deadline(
            body.event_date,
            body.deadline_type,
            body.court_type,
            body.custom_days,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
