from __future__ import annotations

import json
import logging
import os
import sys
from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI

from services.api.version import SENTRY_RELEASE

logger = logging.getLogger(__name__)

_STATUS: dict[str, Any] = {
    "sentry_enabled": False,
    "structured_logging": False,
}


class JsonLogFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "severity": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def monitoring_status() -> dict[str, Any]:
    return dict(_STATUS)


def setup_logging() -> bool:
    log_format = os.getenv("LOG_FORMAT", "").strip().lower()
    level_name = os.getenv("LOG_LEVEL", "info").upper()
    level = getattr(logging, level_name, logging.INFO)

    root = logging.getLogger()
    root.setLevel(level)
    if not root.handlers:
        handler = logging.StreamHandler(sys.stdout)
        root.addHandler(handler)
    else:
        handler = root.handlers[0]

    if log_format in ("json", "gcp"):
        handler.setFormatter(JsonLogFormatter())
        _STATUS["structured_logging"] = True
        logger.info("Logging estruturado JSON ativo (compatível com Cloud Logging)")
    else:
        handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")
        )

    return _STATUS["structured_logging"]


def setup_sentry(app: FastAPI) -> bool:
    dsn = os.getenv("SENTRY_DSN", "").strip()
    if not dsn:
        return False

    try:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        from sentry_sdk.integrations.starlette import StarletteIntegration
    except ImportError:
        logger.warning("SENTRY_DSN definido mas sentry-sdk não instalado")
        return False

    traces_rate = float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1"))
    sentry_sdk.init(
        dsn=dsn,
        integrations=[StarletteIntegration(), FastApiIntegration()],
        environment=os.getenv("SENTRY_ENVIRONMENT", "development"),
        release=os.getenv("SENTRY_RELEASE", SENTRY_RELEASE),
        traces_sample_rate=max(0.0, min(1.0, traces_rate)),
        send_default_pii=False,
    )
    _STATUS["sentry_enabled"] = True
    logger.info("Sentry ativo (env=%s)", os.getenv("SENTRY_ENVIRONMENT", "development"))
    return True


def setup_observability(app: FastAPI) -> dict[str, Any]:
    _STATUS["sentry_enabled"] = False
    _STATUS["structured_logging"] = False
    setup_logging()
    setup_sentry(app)
    return monitoring_status()
