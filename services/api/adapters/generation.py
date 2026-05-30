from __future__ import annotations

import time
from datetime import datetime
from functools import lru_cache
from typing import Any
from uuid import uuid4

import services.api.bootstrap  # noqa: F401

from enhanced_document_generator import EnhancedTemplateLibrary
from jinja2 import Environment

DISCLAIMER = (
    "Minuta de apoio; revisão e assinatura por advogado habilitado obrigatórias."
)


@lru_cache(maxsize=1)
def get_template_library() -> EnhancedTemplateLibrary:
    return EnhancedTemplateLibrary()


def list_templates() -> list[dict[str, Any]]:
    lib = get_template_library()
    return [
        {
            "id": t.id,
            "name": t.name,
            "document_type": t.type.value,
            "legal_area": t.area.value,
            "required_fields": t.required_fields,
            "optional_fields": t.optional_fields,
            "ai_assistance": t.ai_assistance,
            "complexity_level": t.complexity_level,
        }
        for t in lib.templates.values()
    ]


def _prepare_data(raw: dict[str, Any]) -> dict[str, Any]:
    data = raw.copy()
    data.setdefault("local", "São Paulo")
    data.setdefault("data", datetime.now().strftime("%d/%m/%Y"))
    data.setdefault("vara", "1ª")
    data.setdefault("especialidade", "CÍVEL")
    data.setdefault("comarca", "SÃO PAULO")
    data.setdefault("tipo_acao", "AÇÃO INDENIZATÓRIA")
    if "fundamentacao_juridica" not in data:
        data["fundamentacao_juridica"] = (
            "Fundamentação jurídica a ser complementada conforme análise do caso."
        )
    if "pedidos" in data and isinstance(data["pedidos"], str):
        data["pedidos"] = [p.strip() for p in data["pedidos"].split("\n") if p.strip()]
    return data


def _quality_score(content: str, required_fields: list[str]) -> float:
    score = 0.0
    present = sum(1 for f in required_fields if f.lower() in content.lower())
    if required_fields:
        score += (present / len(required_fields)) * 0.5
    indicators = ["artigo", "lei", "código", "pedidos", "fatos"]
    score += min(sum(1 for i in indicators if i in content.lower()) / 3, 1.0) * 0.5
    return round(min(score, 1.0), 2)


def _gemini_enhance(template_id: str, data: dict[str, Any]) -> dict[str, Any]:
    from ai_provider.gemini import generate_text, is_gemini_available
    from legal_core.prompts import load_prompt

    if not is_gemini_available():
        raise ValueError("GEMINI_API_KEY não configurada para enriquecimento.")

    import json

    system = load_prompt("sistema-geracao-peca")
    user = f"""template_id: {template_id}

DADOS_ESTRUTURADOS:
{json.dumps(data, ensure_ascii=False, indent=2)}

Complete apenas campos textuais (fatos, fundamentacao_juridica, pedidos) em JSON
com as mesmas chaves recebidas. Responda só JSON."""
    raw = generate_text(system, user, temperature=0.2, operation="document_generation")
    try:
        import re

        fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", raw)
        parsed = json.loads(fence.group(1).strip() if fence else raw)
        if isinstance(parsed, dict):
            merged = {**data, **parsed}
            return merged
    except (json.JSONDecodeError, AttributeError):
        pass
    return data


def generate_document(
    template_id: str,
    data: dict[str, Any],
    ai_enhancement: bool = False,
) -> dict[str, Any]:
    lib = get_template_library()
    template = lib.get_template(template_id)
    if not template:
        raise ValueError(f"Template não encontrado: {template_id}")

    prepared = _prepare_data(data)
    ai_used = False

    if ai_enhancement and template.ai_assistance:
        prepared = _gemini_enhance(template_id, prepared)
        ai_used = True

    start = time.time()
    env = Environment()
    content = env.from_string(template.template_content).render(**prepared)
    quality = _quality_score(content, template.required_fields)

    return {
        "id": f"doc_{uuid4().hex[:12]}",
        "template_id": template.id,
        "template_name": template.name,
        "document_type": template.type.value,
        "legal_area": template.area.value,
        "content": content,
        "quality_score": quality,
        "metadata": {
            "ai_enhanced": ai_used,
            "generation_time_ms": int((time.time() - start) * 1000),
            "word_count": len(content.split()),
            "disclaimer": DISCLAIMER,
        },
    }
