from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from starlette.requests import Request

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PUBLIC_SUFFIXES = ("/health", "/docs", "/redoc", "/openapi.json")


@dataclass(frozen=True)
class Tenant:
    tenant_id: str
    name: str
    api_key: str
    rate_limit_rpm: int | None = None


def _load_tenants_raw() -> list[dict[str, Any]]:
    path_raw = os.getenv("TENANT_KEYS_PATH", "").strip()
    if path_raw:
        path = Path(path_raw)
        if path.is_file():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                if isinstance(data, list):
                    return data
            except (json.JSONDecodeError, OSError) as exc:
                logger.warning("TENANT_KEYS_PATH inválido: %s", exc)

    json_raw = os.getenv("TENANTS_JSON", "").strip()
    if json_raw:
        try:
            data = json.loads(json_raw)
            if isinstance(data, list):
                return data
        except json.JSONDecodeError as exc:
            logger.warning("TENANTS_JSON inválido: %s", exc)

    return []


def _optional_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        parsed = int(value)
        return parsed if parsed > 0 else None
    except (TypeError, ValueError):
        return None


def load_tenants() -> dict[str, Tenant]:
    tenants: dict[str, Tenant] = {}
    for item in _load_tenants_raw():
        key = str(item.get("api_key", "")).strip()
        tid = str(item.get("tenant_id", "")).strip()
        if not key or not tid:
            continue
        tenants[key] = Tenant(
            tenant_id=tid,
            name=str(item.get("name", tid)),
            api_key=key,
            rate_limit_rpm=_optional_int(item.get("rate_limit_rpm")),
        )
    return tenants


def auth_required() -> bool:
    explicit = os.getenv("AUTH_REQUIRED", "").strip().lower()
    if explicit in ("1", "true", "yes"):
        return True
    if explicit in ("0", "false", "no"):
        return False
    return bool(load_tenants())


def is_public_path(path: str, api_prefix: str) -> bool:
    if path in ("/", "/docs", "/redoc", "/openapi.json"):
        return True
    if path == f"{api_prefix}/health" or path.endswith("/health"):
        return True
    return False


def extract_api_key(request: Request) -> str | None:
    header = request.headers.get("X-API-Key", "").strip()
    if header:
        return header
    auth = request.headers.get("Authorization", "").strip()
    if auth.lower().startswith("bearer "):
        return auth[7:].strip()
    return None


def resolve_tenant(request: Request) -> Tenant | None:
    api_key = extract_api_key(request)
    if not api_key:
        return None
    return load_tenants().get(api_key)


def auth_status() -> dict[str, Any]:
    tenants = load_tenants()
    return {
        "required": auth_required(),
        "tenants_configured": len(tenants),
        "tenant_ids": sorted({t.tenant_id for t in tenants.values()}),
    }
