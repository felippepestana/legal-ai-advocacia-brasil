from __future__ import annotations

import json
import logging
import os
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_STORE = PROJECT_ROOT / "data" / "workflow_store.json"


def store_path() -> Path:
    raw = os.environ.get("WORKFLOW_STORE_PATH", "").strip()
    if raw:
        return Path(raw)
    return DEFAULT_STORE


def _enum_value(obj: Any) -> Any:
    if isinstance(obj, Enum):
        return obj.value
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, dict):
        return {k: _enum_value(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_enum_value(v) for v in obj]
    return obj


def snapshot_engine(engine: Any) -> dict[str, Any]:
    from dataclasses import asdict

    from enhanced_workflow_engine import Workflow, WorkflowExecution

    workflows: dict[str, Any] = {}
    for wid, workflow in engine.workflows.items():
        if isinstance(workflow, Workflow):
            workflows[wid] = _enum_value(asdict(workflow))

    executions: dict[str, Any] = {}
    for eid, execution in engine.executions.items():
        if isinstance(execution, WorkflowExecution):
            executions[eid] = _enum_value(asdict(execution))

    return {
        "version": 1,
        "saved_at": datetime.now().isoformat(),
        "workflows": workflows,
        "executions": executions,
    }


def save_engine(engine: Any) -> None:
    path = store_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    data = snapshot_engine(engine)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.debug("Workflow store salvo em %s", path)


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def restore_engine(engine: Any) -> int:
    path = store_path()
    if not path.is_file():
        return 0

    from enhanced_workflow_engine import (
        StepType,
        TriggerType,
        Workflow,
        WorkflowExecution,
        WorkflowStatus,
        WorkflowStep,
    )

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        logger.warning("Não foi possível carregar workflow store: %s", exc)
        return 0

    count = 0
    for wid, raw in (data.get("workflows") or {}).items():
        try:
            steps = [
                WorkflowStep(
                    id=s["id"],
                    name=s["name"],
                    type=StepType(s["type"]) if isinstance(s["type"], str) else s["type"],
                    config=s.get("config", {}),
                    next_steps=s.get("next_steps", []),
                    conditions=s.get("conditions", []),
                    timeout_minutes=s.get("timeout_minutes", 60),
                    retry_count=s.get("retry_count", 3),
                    required=s.get("required", True),
                )
                for s in raw.get("steps", [])
            ]
            workflow = Workflow(
                id=raw["id"],
                name=raw["name"],
                description=raw.get("description", ""),
                trigger=TriggerType(raw["trigger"]) if isinstance(raw["trigger"], str) else raw["trigger"],
                trigger_config=raw.get("trigger_config", {}),
                steps=steps,
                variables=raw.get("variables", {}),
                created_by=raw.get("created_by", "api"),
                created_at=_parse_datetime(raw.get("created_at")) or datetime.now(),
                updated_at=_parse_datetime(raw.get("updated_at")) or datetime.now(),
                status=WorkflowStatus(raw["status"]) if isinstance(raw["status"], str) else raw["status"],
                tags=raw.get("tags", []),
            )
            engine.workflows[wid] = workflow
            count += 1
        except (KeyError, ValueError) as exc:
            logger.warning("Workflow %s ignorado na restauração: %s", wid, exc)

    for eid, raw in (data.get("executions") or {}).items():
        try:
            execution = WorkflowExecution(
                id=raw["id"],
                workflow_id=raw["workflow_id"],
                status=WorkflowStatus(raw["status"]) if isinstance(raw["status"], str) else raw["status"],
                current_step=raw.get("current_step"),
                start_time=_parse_datetime(raw.get("start_time")) or datetime.now(),
                end_time=_parse_datetime(raw.get("end_time")),
                context=raw.get("context", {}),
                step_results=raw.get("step_results", {}),
                error_log=raw.get("error_log", []),
            )
            engine.executions[eid] = execution
            count += 1
        except (KeyError, ValueError) as exc:
            logger.warning("Execução %s ignorada na restauração: %s", eid, exc)

    return count


def load_engine(engine: Any) -> int:
    return restore_engine(engine)
