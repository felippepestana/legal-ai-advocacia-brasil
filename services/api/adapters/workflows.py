from __future__ import annotations

import asyncio
from typing import Any

import services.api.bootstrap  # noqa: F401

from enhanced_workflow_engine import EnhancedWorkflowEngine
from services.api.workflow_store import load_engine, save_engine

_engine: EnhancedWorkflowEngine | None = None
_engine_loaded = False


def get_engine() -> EnhancedWorkflowEngine:
    global _engine, _engine_loaded
    if _engine is None:
        _engine = EnhancedWorkflowEngine()
    if not _engine_loaded:
        loaded = load_engine(_engine)
        if loaded:
            import logging

            logging.getLogger(__name__).info(
                "Workflow store: %s registro(s) restaurado(s)", loaded
            )
        _engine_loaded = True
    return _engine


def list_templates() -> list[dict[str, str]]:
    return get_engine().template_library.list_templates()


def create_from_template(template_id: str, name: str, variables: dict[str, Any]) -> dict[str, str]:
    workflow_id = get_engine().create_workflow_from_template(template_id, name, variables)
    save_engine(get_engine())
    return {"workflow_id": workflow_id}


async def _persist_after_execution(execution_id: str) -> None:
    """Aguarda conclusão da execução em background e persiste o estado."""
    engine = get_engine()
    for _ in range(60):
        await asyncio.sleep(0.5)
        execution = engine.executions.get(execution_id)
        if execution and execution.end_time:
            save_engine(engine)
            return
    save_engine(engine)


async def execute(workflow_id: str, context: dict[str, Any] | None = None) -> dict[str, str]:
    engine = get_engine()
    execution_id = await engine.execute_workflow(workflow_id, context or {})
    save_engine(engine)
    asyncio.create_task(_persist_after_execution(execution_id))
    return {"execution_id": execution_id}


def get_execution(execution_id: str) -> dict[str, Any]:
    engine = get_engine()
    status = engine.get_execution_status(execution_id)
    if not status:
        raise ValueError(f"Execução não encontrada: {execution_id}")

    execution = engine.executions[execution_id]
    save_engine(engine)
    return {
        **status,
        "step_results": execution.step_results,
    }


def list_workflows() -> list[dict[str, Any]]:
    return get_engine().list_workflows()
