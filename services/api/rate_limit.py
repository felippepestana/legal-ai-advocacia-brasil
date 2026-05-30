from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Any

_BUCKETS: dict[str, tuple[float, int]] = {}


@dataclass(frozen=True)
class RateLimitConfig:
    enabled: bool
    max_requests: int
    window_seconds: int


def rate_limit_enabled() -> bool:
    return os.getenv("RATE_LIMIT_ENABLED", "true").lower() not in ("0", "false", "no")


def default_rate_limit() -> RateLimitConfig:
    try:
        max_requests = max(1, int(os.getenv("RATE_LIMIT_REQUESTS", "120")))
    except ValueError:
        max_requests = 120
    try:
        window_seconds = max(10, int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60")))
    except ValueError:
        window_seconds = 60
    return RateLimitConfig(
        enabled=rate_limit_enabled(),
        max_requests=max_requests,
        window_seconds=window_seconds,
    )


def resolve_limit(tenant_rate_limit_rpm: int | None = None) -> RateLimitConfig:
    base = default_rate_limit()
    if tenant_rate_limit_rpm is not None and tenant_rate_limit_rpm > 0:
        return RateLimitConfig(
            enabled=base.enabled,
            max_requests=tenant_rate_limit_rpm,
            window_seconds=60,
        )
    return base


def _check_rate_limit_redis(
    key: str, config: RateLimitConfig
) -> tuple[bool, int, dict[str, Any]] | None:
    from infra.redis import get_client

    client = get_client()
    if client is None:
        return None

    redis_key = f"ratelimit:{key}"
    count = client.incr(redis_key)
    if count == 1:
        client.expire(redis_key, config.window_seconds)

    ttl = max(1, int(client.ttl(redis_key) or config.window_seconds))
    if count > config.max_requests:
        headers = {
            "Retry-After": str(ttl),
            "X-RateLimit-Limit": str(config.max_requests),
            "X-RateLimit-Remaining": "0",
            "X-RateLimit-Reset": str(int(time.time()) + ttl),
        }
        return False, ttl, headers

    remaining = max(0, config.max_requests - count)
    headers = {
        "X-RateLimit-Limit": str(config.max_requests),
        "X-RateLimit-Remaining": str(remaining),
        "X-RateLimit-Reset": str(int(time.time()) + ttl),
    }
    return True, 0, headers


def check_rate_limit(key: str, config: RateLimitConfig) -> tuple[bool, int, dict[str, Any]]:
    """Retorna (permitido, retry_after_segundos, headers)."""
    if not config.enabled:
        return True, 0, {}

    redis_result = _check_rate_limit_redis(key, config)
    if redis_result is not None:
        return redis_result

    now = time.time()
    window_start, count = _BUCKETS.get(key, (now, 0))

    if now - window_start >= config.window_seconds:
        window_start = now
        count = 0

    if count >= config.max_requests:
        retry_after = max(1, int(config.window_seconds - (now - window_start)))
        headers = {
            "Retry-After": str(retry_after),
            "X-RateLimit-Limit": str(config.max_requests),
            "X-RateLimit-Remaining": "0",
            "X-RateLimit-Reset": str(int(window_start + config.window_seconds)),
        }
        return False, retry_after, headers

    _BUCKETS[key] = (window_start, count + 1)
    remaining = max(0, config.max_requests - count - 1)
    headers = {
        "X-RateLimit-Limit": str(config.max_requests),
        "X-RateLimit-Remaining": str(remaining),
        "X-RateLimit-Reset": str(int(window_start + config.window_seconds)),
    }
    return True, 0, headers


def reset_buckets() -> None:
    """Usado em testes."""
    _BUCKETS.clear()
    from infra.redis import get_client

    client = get_client()
    if client is not None:
        for key in client.scan_iter("ratelimit:*"):
            client.delete(key)


def rate_limit_status() -> dict[str, Any]:
    from infra.redis import redis_status

    cfg = default_rate_limit()
    redis = redis_status()
    return {
        "enabled": cfg.enabled,
        "max_requests": cfg.max_requests,
        "window_seconds": cfg.window_seconds,
        "backend": redis["backend"],
        "redis_connected": redis["connected"],
    }
