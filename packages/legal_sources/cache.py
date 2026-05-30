from __future__ import annotations

import hashlib
import json
import logging
import os
import time
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_MEMORY: dict[str, tuple[float, dict[str, Any]]] = {}


def cache_enabled() -> bool:
    return os.getenv("SEARCH_CACHE_ENABLED", "true").lower() not in ("0", "false", "no")


def cache_ttl_seconds() -> int:
    try:
        return max(60, int(os.getenv("SEARCH_CACHE_TTL_SECONDS", "900")))
    except ValueError:
        return 900


def _cache_dir() -> Path | None:
    raw = os.getenv("SEARCH_CACHE_DIR", "").strip()
    if raw:
        return Path(raw)
    if os.getenv("SEARCH_CACHE_PERSIST", "false").lower() in ("1", "true", "yes"):
        from legal_core.paths import PROJECT_ROOT

        return PROJECT_ROOT / "data" / "search_cache"
    return None


def make_cache_key(
    query: str,
    search_type: str,
    tribunals: list[str] | None,
    *,
    use_datajud: bool,
    use_legislation: bool,
    use_jurisprudencias: bool,
) -> str:
    payload = {
        "query": query.strip().lower(),
        "search_type": search_type.lower(),
        "tribunals": sorted(tribunals or []),
        "use_datajud": use_datajud,
        "use_legislation": use_legislation,
        "use_jurisprudencias": use_jurisprudencias,
    }
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _redis_get(key: str) -> dict[str, Any] | None:
    from infra.redis import get_client

    client = get_client()
    if client is None:
        return None
    raw = client.get(f"searchcache:{key}")
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


def _redis_set(key: str, payload: dict[str, Any], ttl: int) -> None:
    from infra.redis import get_client

    client = get_client()
    if client is None:
        return
    client.set(f"searchcache:{key}", json.dumps(payload, ensure_ascii=False), ex=ttl)


def get_cached(key: str) -> dict[str, Any] | None:
    if not cache_enabled():
        return None

    now = time.time()
    ttl = cache_ttl_seconds()

    redis_data = _redis_get(key)
    if redis_data is not None:
        _MEMORY[key] = (now, redis_data)
        return {**redis_data, "cache_hit": True}

    entry = _MEMORY.get(key)
    if entry and now - entry[0] < ttl:
        return {**entry[1], "cache_hit": True}

    cache_dir = _cache_dir()
    if cache_dir:
        path = cache_dir / f"{key}.json"
        if path.is_file() and now - path.stat().st_mtime < ttl:
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                _MEMORY[key] = (now, data)
                return {**data, "cache_hit": True}
            except (json.JSONDecodeError, OSError) as exc:
                logger.debug("Cache inválido %s: %s", key, exc)

    return None


def set_cached(key: str, payload: dict[str, Any]) -> None:
    if not cache_enabled():
        return

    stored = {k: v for k, v in payload.items() if k != "cache_hit"}
    now = time.time()
    ttl = cache_ttl_seconds()
    _MEMORY[key] = (now, stored)

    _redis_set(key, stored, ttl)

    cache_dir = _cache_dir()
    if cache_dir:
        try:
            cache_dir.mkdir(parents=True, exist_ok=True)
            (cache_dir / f"{key}.json").write_text(
                json.dumps(stored, ensure_ascii=False),
                encoding="utf-8",
            )
        except OSError as exc:
            logger.debug("Não foi possível persistir cache: %s", exc)


def clear_cache() -> None:
    """Usado em testes."""
    _MEMORY.clear()
    from infra.redis import get_client

    client = get_client()
    if client is not None:
        for key in client.scan_iter("searchcache:*"):
            client.delete(key)


def cache_status() -> dict[str, Any]:
    from infra.redis import redis_status

    redis = redis_status()
    return {
        "enabled": cache_enabled(),
        "ttl_seconds": cache_ttl_seconds(),
        "backend": redis["backend"],
        "redis_connected": redis["connected"],
    }
