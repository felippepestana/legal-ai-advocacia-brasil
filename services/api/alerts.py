from __future__ import annotations

import csv
import io
import json
import logging
import os
from typing import Any

import requests

logger = logging.getLogger(__name__)


def slack_alerts_enabled() -> bool:
    return bool(os.getenv("SLACK_WEBHOOK_URL", "").strip())


def _webhook_url() -> str | None:
    url = os.getenv("SLACK_WEBHOOK_URL", "").strip()
    return url or None


def notify_slack(
    *,
    title: str,
    message: str,
    level: str = "error",
    fields: dict[str, str] | None = None,
) -> bool:
    """Envia alerta ao Slack via Incoming Webhook. Retorna True se enviado."""
    if os.getenv("SLACK_ALERTS_ENABLED", "true").lower() in ("0", "false", "no"):
        return False

    url = _webhook_url()
    if not url:
        return False

    emoji = {"error": ":rotating_light:", "warning": ":warning:", "info": ":information_source:"}.get(
        level, ":bell:"
    )
    blocks: list[dict[str, Any]] = [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": f"{emoji} {title}", "emoji": True},
        },
        {"type": "section", "text": {"type": "mrkdwn", "text": message}},
    ]

    if fields:
        field_blocks = [
            {"type": "mrkdwn", "text": f"*{key}*\n{value}"} for key, value in fields.items()
        ]
        blocks.append({"type": "section", "fields": field_blocks[:10]})

    payload = {
        "text": f"{title}: {message}",
        "blocks": blocks,
    }

    try:
        response = requests.post(url, json=payload, timeout=5)
        response.raise_for_status()
        return True
    except requests.RequestException as exc:
        logger.warning("Falha ao enviar alerta Slack: %s", exc)
        return False


def notify_ai_failure(event: dict[str, Any]) -> bool:
    """Alerta Slack quando uma consulta IA falha (complementa Sentry)."""
    if event.get("success") is not False:
        return False

    return notify_slack(
        title="Falha em consulta IA",
        message="Uma operação de IA falhou na plataforma jurídica.",
        level="error",
        fields={
            "Tenant": str(event.get("tenant_id", "—")),
            "Operação": str(event.get("operation", "—")),
            "Modelo": f"{event.get('backend', '—')}/{event.get('model', '—')}",
            "Latência": f"{event.get('latency_ms', 0)} ms",
            "Erro": str(event.get("error", "desconhecido"))[:300],
            "Prompt hash": str(event.get("prompt_hash", "—")),
        },
    )
