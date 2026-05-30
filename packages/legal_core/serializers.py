"""Converte resultados dos módulos legados para JSON da API."""

from __future__ import annotations

import re
from typing import Any

from legal_core.validators.peticao_inicial import PeticaoValidationResult, validate_peticao_inicial

DISCLAIMER = (
    "Análise de apoio; não constitui parecer jurídico nem substitui advogado."
)


def _entity_type_id(label: str) -> str:
    mapping = {
        "Pessoa Física": "pessoa_fisica",
        "Pessoa Jurídica": "pessoa_juridica",
        "Número de Processo": "processo_cnj",
        "CPF": "cpf",
        "CNPJ": "cnpj",
        "OAB": "oab",
        "Valor Monetário": "valor_monetario",
        "Data": "data",
    }
    return mapping.get(label, re.sub(r"\s+", "_", label.lower()))


def _document_type_id(display_name: str) -> str:
    slug = display_name.lower()
    slug = (
        slug.replace("ç", "c")
        .replace("ã", "a")
        .replace("á", "a")
        .replace("é", "e")
        .replace("í", "i")
        .replace("ó", "o")
        .replace("õ", "o")
        .replace("ú", "u")
    )
    slug = re.sub(r"[^a-z0-9]+", "_", slug).strip("_")
    return slug or "outros"


def analysis_to_api_payload(
    analysis: Any,
    legal_area: str | None = None,
    source_text: str | None = None,
) -> dict[str, Any]:
    doc_type_id = _document_type_id(
        analysis.document_type.value
        if hasattr(analysis.document_type, "value")
        else str(analysis.document_type)
    )

    entities = [
        {
            "type": _entity_type_id(e.type.value if hasattr(e.type, "value") else str(e.type)),
            "text": e.text,
            "normalized_value": getattr(e, "normalized_value", "") or e.text,
            "confidence": float(e.confidence),
            "context": getattr(e, "context", "") or "",
        }
        for e in analysis.entities
    ]

    concepts = [
        {
            "concept": c.concept,
            "category": c.category,
            "confidence": float(c.confidence),
            "related_articles": c.related_articles or [],
        }
        for c in analysis.legal_concepts
    ]

    gaps: list[str] = []
    if doc_type_id == "peticao_inicial":
        text_for_cpc = source_text or _reconstruct_text_from_analysis(analysis)
        validation = validate_peticao_inicial(text_for_cpc, tipo_peca=doc_type_id)
        gaps = validation.correcoes_prioritarias

    return {
        "document_type": doc_type_id,
        "legal_area": legal_area,
        "confidence": float(analysis.confidence),
        "entities": entities,
        "legal_concepts": concepts,
        "summary": analysis.summary,
        "key_points": analysis.key_points,
        "gaps": gaps,
        "opportunities": [],
        "metadata": {
            **(analysis.metadata or {}),
            "disclaimer": DISCLAIMER,
            "processing_time_ms": int(analysis.processing_time * 1000),
        },
    }


def _reconstruct_text_from_analysis(analysis: Any) -> str:
    """Fallback quando só temos entidades — validação CPC limitada."""
    parts = [analysis.summary] + analysis.key_points
    for e in analysis.entities:
        parts.append(e.text)
    return "\n".join(p for p in parts if p)


def validation_to_api_payload(result: PeticaoValidationResult) -> dict[str, Any]:
    return {
        "tipo_peca": result.tipo_peca,
        "compliance_score": result.compliance_score,
        "itens": [
            {
                "requisito": i.requisito,
                "status": i.status,
                "severidade": i.severidade,
                "trecho_ou_observacao": i.trecho_ou_observacao,
            }
            for i in result.itens
        ],
        "correcoes_prioritarias": result.correcoes_prioritarias,
    }
