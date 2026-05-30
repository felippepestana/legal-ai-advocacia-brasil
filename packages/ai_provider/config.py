from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Literal

AIBackend = Literal["api_key", "vertex"]


@dataclass(frozen=True)
class AIConfig:
    backend: AIBackend
    model: str
    api_key: str | None = None
    project: str | None = None
    location: str | None = None

    @classmethod
    def from_env(cls) -> AIConfig | None:
        model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash").strip()
        backend_pref = os.getenv("AI_BACKEND", "").strip().lower()

        api_key = (os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or "").strip()
        project = os.getenv("GOOGLE_CLOUD_PROJECT", "").strip()
        location = os.getenv("VERTEX_LOCATION", "us-central1").strip() or "us-central1"

        if backend_pref == "vertex":
            if not project:
                return None
            return cls(backend="vertex", model=model, project=project, location=location)

        if backend_pref == "api_key":
            if not api_key:
                return None
            return cls(backend="api_key", model=model, api_key=api_key)

        # Auto: Vertex em produção (projeto GCP sem depender de API key exposta)
        if project and not api_key:
            return cls(backend="vertex", model=model, project=project, location=location)

        if api_key:
            return cls(backend="api_key", model=model, api_key=api_key)

        if project:
            return cls(backend="vertex", model=model, project=project, location=location)

        return None


def get_ai_status() -> dict[str, str | bool | None]:
    cfg = AIConfig.from_env()
    if not cfg:
        return {
            "available": False,
            "backend": None,
            "model": None,
            "project": None,
            "location": None,
        }
    return {
        "available": True,
        "backend": cfg.backend,
        "model": cfg.model,
        "project": cfg.project if cfg.backend == "vertex" else None,
        "location": cfg.location if cfg.backend == "vertex" else None,
    }
