"""
Validação determinística — requisitos do art. 319 CPC/2015 (petição inicial).
Alinhado a advocacia-brasil-hub/.cursor/skills/validacao-peticao-cpc
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass


@dataclass
class RequirementCheck:
    requisito: str
    status: str  # ok | parcial | ausente
    severidade: str  # critical | warning | info
    trecho_ou_observacao: str


@dataclass
class PeticaoValidationResult:
    tipo_peca: str
    compliance_score: int
    itens: list[RequirementCheck]
    correcoes_prioritarias: list[str]


def _normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    return text.lower()


# (rótulo, severidade, padrões regex — qualquer match conta como ok)
_CPC_319_CHECKS: list[tuple[str, str, list[str]]] = [
    (
        "Juízo a que é dirigida",
        "critical",
        [r"excelent", r"meritissim", r"juiz", r"juizo", r"vara", r"doutor"],
    ),
    (
        "Qualificação das partes (autor e réu)",
        "critical",
        [r"cpf", r"cnpj", r"qualificad", r"residente", r"domiciliad", r"inscrit"],
    ),
    (
        "Fatos e fundamentos jurídicos do pedido",
        "critical",
        [r"dos fatos", r"fatos", r"fundament", r"direito", r"pedido"],
    ),
    (
        "Pedido com especificações",
        "critical",
        [r"dos pedidos", r"pede", r"requer", r"conden"],
    ),
    (
        "Valor da causa",
        "critical",
        [r"valor da causa", r"da causa"],
    ),
    (
        "Provas",
        "warning",
        [r"provas", r"protesta", r"documentos", r"testemunh"],
    ),
    (
        "Audiência de conciliação/mediação",
        "warning",
        [r"conciliac", r"mediac", r"audiencia"],
    ),
    (
        "Assinatura e OAB",
        "critical",
        [r"oab", r"advogad", r"assinatur"],
    ),
    (
        "Data e local",
        "info",
        [r"\d{1,2}\s+de\s+\w+\s+de\s+\d{4}", r"sao paulo", r"comarca"],
    ),
]


def validate_peticao_inicial(content: str, tipo_peca: str = "peticao_inicial") -> PeticaoValidationResult:
    normalized = _normalize(content)
    itens: list[RequirementCheck] = []
    weights = {"critical": 3, "warning": 2, "info": 1}
    earned = 0
    total = 0

    for requisito, severidade, patterns in _CPC_319_CHECKS:
        total += weights[severidade]
        matched = None
        for pattern in patterns:
            m = re.search(pattern, normalized, re.IGNORECASE)
            if m:
                matched = m.group(0)[:80]
                break

        if matched:
            status = "ok"
            earned += weights[severidade]
            obs = f"Indício encontrado: «{matched}»"
        else:
            status = "ausente"
            obs = "Requisito não identificado no texto — revisar manualmente."

        itens.append(
            RequirementCheck(
                requisito=requisito,
                status=status,
                severidade=severidade,
                trecho_ou_observacao=obs,
            )
        )

    score = round(100 * earned / total) if total else 0
    correcoes = [
        f"{i.requisito}: {i.trecho_ou_observacao}"
        for i in itens
        if i.status != "ok" and i.severidade in ("critical", "warning")
    ]

    return PeticaoValidationResult(
        tipo_peca=tipo_peca,
        compliance_score=score,
        itens=itens,
        correcoes_prioritarias=correcoes,
    )
