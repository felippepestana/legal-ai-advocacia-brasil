from __future__ import annotations

import logging
import os
import re
from typing import Any

import requests

from legal_sources.base import SearchHit

logger = logging.getLogger(__name__)

DATAJUD_BASE = "https://api-publica.datajud.cnj.jus.br"
DEFAULT_API_KEY = (
    "cDZHYzlZa0JadVREZDJCendQbXY6SkJlTzNjLV9TRENyQk1RdnFKZGRQdw=="
)

# Tribunais mais usados em advocacia cível/trabalhista
TRIBUNAL_ALIASES: dict[str, str] = {
    "stj": "stj",
    "stf": "stf",
    "tst": "tst",
    "tjsp": "tjsp",
    "tjrj": "tjrj",
    "tjmg": "tjmg",
    "trf1": "trf1",
    "trf2": "trf2",
    "trf3": "trf3",
    "trf4": "trf4",
    "trf5": "trf5",
    "trt2": "trt2",
    "trt15": "trt15",
}

DEFAULT_TRIBUNALS = ("stj", "stf", "tjsp")


def _api_key() -> str:
    return os.environ.get("DATAJUD_API_KEY", DEFAULT_API_KEY).strip()


def _build_query(text: str) -> dict[str, Any]:
    terms = [t for t in re.findall(r"\w+", text.lower()) if len(t) > 2][:8]
    if not terms:
        return {"match_all": {}}
    return {
        "bool": {
            "should": [
                {"match": {"classe.nome": {"query": text, "boost": 2}}},
                {"match": {"movimentos.nome": text}},
                *[{"match": {"assuntos.nome": term}} for term in terms[:4]],
            ],
            "minimum_should_match": 1,
        }
    }


def _parse_date(value: str | None) -> Any:
    if not value:
        return None
    try:
        from datetime import datetime

        clean = value.replace("Z", "+00:00")
        if len(clean) >= 10 and clean[4] == "-":
            return datetime.fromisoformat(clean[:19])
        if len(value) >= 8 and value.isdigit():
            return datetime.strptime(value[:8], "%Y%m%d")
    except (ValueError, TypeError):
        return None
    return None


def _hit_from_source(hit: dict[str, Any], tribunal: str) -> SearchHit | None:
    src = hit.get("_source") or {}
    numero = src.get("numeroProcesso") or hit.get("_id", "")
    classe = (src.get("classe") or {}).get("nome", "Processo")
    tribunal_nome = src.get("tribunal") or tribunal.upper()
    movimentos = src.get("movimentos") or []
    ultimo = movimentos[-1] if movimentos else {}
    mov_nome = ultimo.get("nome", "")
    orgao = (ultimo.get("orgaoJulgador") or {}).get("nome", "")

    content_parts = [
        f"Classe: {classe}.",
        f"Tribunal: {tribunal_nome}.",
    ]
    if mov_nome:
        content_parts.append(f"Última movimentação: {mov_nome}.")
    if orgao:
        content_parts.append(f"Órgão: {orgao}.")
    assuntos = src.get("assuntos") or []
    if assuntos:
        nomes = [a.get("nome") for a in assuntos[:3] if a.get("nome")]
        if nomes:
            content_parts.append("Assuntos: " + "; ".join(nomes) + ".")

    score = float(hit.get("_score") or 0)
    relevance = min(1.0, 0.35 + score * 0.05) if score else 0.55

    return SearchHit(
        id=f"datajud_{tribunal}_{numero}",
        title=f"{classe} — {numero}",
        content=" ".join(content_parts),
        source=f"DataJud ({tribunal_nome})",
        provider="datajud",
        court=tribunal_nome,
        date=_parse_date(src.get("dataAjuizamento") or src.get("dataHoraUltimaAtualizacao")),
        url="https://www.cnj.jus.br/sistemas/datajud/",
        relevance_score=relevance,
        metadata={
            "numero_processo": numero,
            "grau": src.get("grau"),
            "datajud_index": hit.get("_index"),
        },
    )


def search_datajud(
    query: str,
    *,
    tribunals: list[str] | None = None,
    size_per_tribunal: int = 5,
    timeout: int = 25,
) -> tuple[list[SearchHit], list[str]]:
    """Consulta API pública DataJud (CNJ). Retorna hits e avisos."""
    warnings: list[str] = []
    hits: list[SearchHit] = []

    raw_tribunals = tribunals or list(DEFAULT_TRIBUNALS)
    resolved: list[str] = []
    for t in raw_tribunals:
        key = t.lower().replace("api_publica_", "").strip()
        alias = TRIBUNAL_ALIASES.get(key, key)
        if alias:
            resolved.append(alias)

    if not resolved:
        resolved = list(DEFAULT_TRIBUNALS)

    headers = {
        "Authorization": f"APIKey {_api_key()}",
        "Content-Type": "application/json",
    }
    body = {"size": size_per_tribunal, "query": _build_query(query)}

    for tribunal in resolved:
        url = f"{DATAJUD_BASE}/api_publica_{tribunal}/_search"
        try:
            response = requests.post(url, headers=headers, json=body, timeout=timeout)
            if response.status_code == 401:
                warnings.append("DataJud: chave API inválida ou expirada.")
                break
            if response.status_code >= 400:
                warnings.append(f"DataJud {tribunal.upper()}: HTTP {response.status_code}")
                continue
            data = response.json()
            for hit in data.get("hits", {}).get("hits", []):
                parsed = _hit_from_source(hit, tribunal)
                if parsed:
                    hits.append(parsed)
        except requests.RequestException as exc:
            logger.warning("DataJud %s: %s", tribunal, exc)
            warnings.append(f"DataJud {tribunal.upper()}: indisponível ({exc.__class__.__name__})")

    return hits, warnings
