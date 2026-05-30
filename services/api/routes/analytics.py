from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from services.api.adapters import analytics as analytics_adapter
from services.api.schemas import AnalyticsRunRequest

router = APIRouter()


@router.get("/types")
def analysis_types() -> dict:
    return {"types": analytics_adapter.list_analysis_types()}


@router.post("/run")
def run_analysis(body: AnalyticsRunRequest) -> dict:
    try:
        return analytics_adapter.run_analysis(
            body.analysis_type,
            body.num_cases,
            export_charts=body.export_charts,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/charts/{filename}")
def get_chart(filename: str) -> FileResponse:
    path = analytics_adapter.resolve_chart_file(filename)
    if not path:
        raise HTTPException(status_code=404, detail="Gráfico não encontrado")
    return FileResponse(path, media_type="image/png")
