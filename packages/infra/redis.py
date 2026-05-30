from __future__ import annotations

import logging
import os
from typing import Any

logger = logging.getLogger(__name__)

_client: Any | None = None
_client_checked = False


def redis_url() -> str | None:
    raw = os.getenv("REDIS_URL", "").strip()
    return raw or None


def redis_enabled() -> bool:
    return redis_url() is not None


def get_client() -> Any | None:
    """Cliente Redis lazy; None se REDIS_URL ausente ou conexão falhar."""
    global _client, _client_checked

    if not redis_enabled():
        return None

    if _client_checked:
        return _client

    _client_checked = True
    try:
        import redis

        _client = redis.from_url(redis_url(), decode_responses=True)
        _client.ping()
        logger.info("Redis conectado")
    except Exception as exc:
        logger.warning("Redis indisponível, usando fallback em memória: %s", exc)
        _client = None

    return _client


def reset_client() -> None:
    """Usado em testes."""
    global _client, _client_checked
    _client = None
    _client_checked = False


def redis_status() -> dict[str, Any]:
    enabled = redis_enabled()
    connected = False
    if enabled:
        try:
            client = get_client()
            connected = client is not None and client.ping()
        except Exception:
            connected = False
    backend = "memory"
    if enabled and connected:
        backend = "redis"
    elif enabled:
        backend = "memory_fallback"
    return {
        "enabled": enabled,
        "connected": connected,
        "backend": backend,
    }
