from __future__ import annotations

import logging
import re
from typing import Any

import requests

from legal_sources.base import SearchHit

logger = logging.getLogger(__name__)

SENADO_BASE = "https://legis.senado.leg.br/dadosabertos"
HEADERS = {"Accept": "application/json"}

# Padrões: lei 8078, lei 8.078/90, decreto 9950/2019
LAW_PATTERN = re.compile(
    r"\b(lei|decreto|mp|medida\s+provis[oó]ria|emenda\s+constitucional|ec)\s*"
    r"[\s.nºº°]*(\d[\d.\s]*)(?:\s*/\s*(\d{2,4}))?",
    re.IGNORECASE,
)


def _normalize_number(raw: str) -> str:
    digits = re.sub(r"\D", "", raw)
    return digits.lstrip("0") or digits


def _parse_law_queries(text: str) -> list[dict[str, str]]:
    found: list[dict[str, str]] = []
    for match in LAW_PATTERN.finditer(text):
        tipo = match.group(1).upper()
        tipo = "LEI" if "LEI" in tipo else tipo.split()[0][:3]
        if "MEDIDA" in match.group(1).upper():
            tipo = "MPV"
        if "EMENDA" in match.group(1).upper():
            tipo = "EC"
        numero = _normalize_number(match.group(2))
        ano = match.group(3)
        if ano and len(ano) == 2:
            ano = f"19{ano}" if int(ano) > 50 else f"20{ano}"
        params: dict[str, str] = {"sigla": tipo, "numero": numero}
        if ano:
            params["ano"] = ano
        found.append(params)
    return found


def _extract_documents(payload: dict[str, Any]) -> list[dict[str, Any]]:
    docs = (payload.get("ListaDocumento") or {}).get("documentos") or {}
    documento = docs.get("documento")
    if not documento:
        return []
    if isinstance(documento, list):
        return documento
    return [documento]


def _hit_from_norma(doc: dict[str, Any]) -> SearchHit:
    ementa = doc.get("ementa") or doc.get("normaNome") or ""
    norma = doc.get("normaNome") or doc.get("norma") or "Norma federal"
    numero = doc.get("numero", "")
    url = f"https://www.lexml.gov.br/urn/{doc.get('norma', '')}" if doc.get("norma") else "https://www.lexml.gov.br/"
    return SearchHit(
        id=f"senado_leg_{doc.get('id', norma)}",
        title=norma,
        content=ementa or f"Norma federal {norma} (sem ementa resumida na API).",
        source="Legislação federal (Senado / rede LexML)",
        provider="senado_legislacao",
        url=url,
        relevance_score=0.85,
        metadata={
            "apelido": doc.get("apelido"),
            "data_assinatura": doc.get("dataassinatura"),
            "tipo": doc.get("tipo"),
        },
    )


def search_senado_legislacao(query: str, *, timeout: int = 20) -> tuple[list[SearchHit], list[str]]:
    """
    Pesquisa normas via API Dados Abertos do Senado (integrante da rede LexML).
  """
    warnings: list[str] = []
    hits: list[SearchHit] = []

    law_queries = _parse_law_queries(query)
    if not law_queries:
        # Busca por termos no catálogo e tenta uma norma conhecida se houver número isolado
        try:
            response = requests.get(
                f"{SENADO_BASE}/legislacao/termos",
                params={"termo": query[:80]},
                headers=HEADERS,
                timeout=timeout,
            )
            if response.ok:
                warnings.append(
                    "Legislação: informe número da norma (ex.: lei 8078/1990) para busca direta; "
                    "catálogo de termos consultado."
                )
        except requests.RequestException:
            pass
        return hits, warnings

    for params in law_queries[:3]:
        try:
            response = requests.get(
                f"{SENADO_BASE}/legislacao/lista",
                params=params,
                headers=HEADERS,
                timeout=timeout,
            )
            if not response.ok:
                warnings.append(f"Senado legislação: HTTP {response.status_code} para {params}")
                continue
            for doc in _extract_documents(response.json()):
                hits.append(_hit_from_norma(doc))
        except requests.RequestException as exc:
            logger.warning("Senado legislação: %s", exc)
            warnings.append(f"Senado legislação: indisponível ({exc.__class__.__name__})")

    return hits, warnings
