from fastapi import APIRouter, HTTPException

from services.api.adapters import workflows as workflows_adapter
from services.api.schemas import CreateWorkflowRequest, ExecuteWorkflowRequest

router = APIRouter()


@router.get("/templates")
def workflow_templates() -> dict:
    return {"templates": workflows_adapter.list_templates()}


@router.get("/")
def list_workflows() -> dict:
    return {"workflows": workflows_adapter.list_workflows()}


@router.post("/create")
def create_workflow(body: CreateWorkflowRequest) -> dict:
    try:
        return workflows_adapter.create_from_template(
            body.template_id, body.name, body.variables
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/execute")
async def execute_workflow(body: ExecuteWorkflowRequest) -> dict:
    try:
        return await workflows_adapter.execute(body.workflow_id, body.context)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/executions/{execution_id}")
def get_execution(execution_id: str) -> dict:
    try:
        return workflows_adapter.get_execution(execution_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
