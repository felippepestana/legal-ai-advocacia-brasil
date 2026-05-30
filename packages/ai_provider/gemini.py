"""
Camada opcional Gemini — API key (dev) ou Vertex AI (produção).
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

from ai_provider.client import generate_content
from ai_provider.config import AIConfig, get_ai_status
from legal_core.prompts import load_prompt


@dataclass
class GeminiConfig:
    """Compatibilidade com imports antigos."""

    api_key: str
    model: str = "gemini-2.0-flash"

    @classmethod
    def from_env(cls) -> GeminiConfig | None:
        cfg = AIConfig.from_env()
        if not cfg:
            return None
        if cfg.backend == "api_key" and cfg.api_key:
            return cls(api_key=cfg.api_key, model=cfg.model)
        if cfg.backend == "vertex":
            return cls(api_key="vertex", model=cfg.model)
        return None


def is_gemini_available() -> bool:
    return AIConfig.from_env() is not None


def _extract_json(text: str) -> dict[str, Any]:
    text = text.strip()
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if fence:
        text = fence.group(1).strip()
    return json.loads(text)


def _require_config() -> AIConfig:
    config = AIConfig.from_env()
    if not config:
        raise RuntimeError(
            "IA não configurada. Dev: GEMINI_API_KEY. "
            "Produção: GOOGLE_CLOUD_PROJECT + VERTEX_LOCATION + ADC (AI_BACKEND=vertex)."
        )
    return config


def enhance_document_analysis(
    document_text: str,
    base_payload: dict[str, Any],
    legal_area: str | None = None,
) -> dict[str, Any]:
    config = _require_config()
    system = load_prompt("sistema-analise-documento")
    area_line = f"Área informada: {legal_area}\n" if legal_area else ""
    user = f"""{area_line}
<<<DOCUMENTO>>>
{document_text}
<<<FIM_DOCUMENTO>>>

Análise preliminar (motor local — use como referência, corrija se necessário):
{json.dumps(base_payload, ensure_ascii=False, indent=2)}

Produza JSON completo no schema da análise documental."""

    raw = generate_content(
        config, system, user, temperature=0.2, max_output_tokens=4096, operation="document_enhance"
    )
    enhanced = _extract_json(raw)

    merged = {**base_payload, **{k: v for k, v in enhanced.items() if v is not None}}
    merged["metadata"] = {
        **(base_payload.get("metadata") or {}),
        **(enhanced.get("metadata") or {}),
        "ai_enhanced": True,
        "ai_model": config.model,
        "ai_backend": config.backend,
    }
    return merged


def generate_text(
    system_prompt: str,
    user_prompt: str,
    *,
    temperature: float = 0.3,
    max_output_tokens: int = 4096,
    operation: str = "generate",
) -> str:
    config = _require_config()
    return generate_content(
        config,
        system_prompt,
        user_prompt,
        temperature=temperature,
        max_output_tokens=max_output_tokens,
        operation=operation,
    )


def synthesize_search_results(query: str, results: list[dict[str, Any]]) -> str:
    system = load_prompt("sistema-pesquisa-normativa")
    fontes = json.dumps(results[:8], ensure_ascii=False, indent=2)
    user = f"""Consulta: {query}

FONTES_FORNECIDAS:
{fontes}

Produza resumo executivo em markdown, citando apenas as fontes acima."""
    return generate_text(system, user, temperature=0.2, operation="search_synthesis")


__all__ = [
    "GeminiConfig",
    "get_ai_status",
    "is_gemini_available",
    "enhance_document_analysis",
    "generate_text",
    "synthesize_search_results",
]
