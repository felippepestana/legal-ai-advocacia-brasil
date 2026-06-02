from __future__ import annotations

import csv
import hashlib
import io
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Logger dedicado à trilha de auditoria. Em produção (LOG_FORMAT=json) cada
# evento é serializado pelo JsonLogFormatter e persistido de forma durável no
# Cloud Logging — o disco local (data/audit/) é efêmero no Cloud Run.
audit_logger = logging.getLogger("ai_audit")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_AUDIT_DIR = PROJECT_ROOT / "data" / "audit"


def audit_dir() -> Path:
    raw = os.environ.get("AUDIT_LOG_DIR", "").strip()
    if raw:
        return Path(raw)
    return DEFAULT_AUDIT_DIR


def _audit_file() -> Path:
    day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return audit_dir() / f"ai_audit_{day}.jsonl"


def _hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def log_ai_event(
    *,
    tenant_id: str,
    operation: str,
    model: str,
    backend: str,
    system_prompt: str,
    user_prompt: str,
    latency_ms: int,
    success: bool,
    error: str | None = None,
    output_chars: int = 0,
) -> None:
    if os.getenv("AI_AUDIT_ENABLED", "true").lower() in ("0", "false", "no"):
        return

    event: dict[str, Any] = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "tenant_id": tenant_id,
        "operation": operation,
        "model": model,
        "backend": backend,
        "latency_ms": latency_ms,
        "prompt_hash": _hash_text(f"{system_prompt}\n---\n{user_prompt}"),
        "system_chars": len(system_prompt),
        "user_chars": len(user_prompt),
        "output_chars": output_chars,
        "success": success,
    }
    if error:
        event["error"] = error[:500]

    # Trilha durável: emite o evento estruturado para o Cloud Logging.
    # Independe do disco local, sobrevivendo a reinícios/revisões do Cloud Run.
    try:
        audit_logger.info("ai_audit", extra={"audit_event": event})
    except Exception as exc:  # nunca derruba a requisição por falha de log
        logger.debug("Falha ao emitir audit log estruturado: %s", exc)

    path = _audit_file()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, ensure_ascii=False) + "\n")
    except OSError as exc:
        logger.warning("Falha ao gravar audit log: %s", exc)
        return

    if not success:
        try:
            from services.api.alerts import notify_ai_failure

            notify_ai_failure(event)
        except Exception as exc:
            logger.debug("Alerta Slack ignorado: %s", exc)


def read_recent_events(limit: int = 50) -> list[dict[str, Any]]:
    path = _audit_file()
    if not path.is_file():
        return []
    lines = path.read_text(encoding="utf-8").strip().splitlines()
    events: list[dict[str, Any]] = []
    for line in lines[-limit:]:
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return events


def read_events_for_tenant(tenant_id: str, limit: int = 500) -> list[dict[str, Any]]:
    pool = read_recent_events(limit=max(limit * 4, 500))
    filtered = [e for e in pool if e.get("tenant_id") == tenant_id]
    return filtered[-limit:]


CSV_COLUMNS = (
    "ts",
    "tenant_id",
    "operation",
    "model",
    "backend",
    "latency_ms",
    "prompt_hash",
    "system_chars",
    "user_chars",
    "output_chars",
    "success",
    "error",
)


def events_to_csv(events: list[dict[str, Any]]) -> str:
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=CSV_COLUMNS, extrasaction="ignore")
    writer.writeheader()
    for event in events:
        row = {col: event.get(col, "") for col in CSV_COLUMNS}
        row["success"] = "true" if event.get("success") else "false"
        writer.writerow(row)
    return buffer.getvalue()
