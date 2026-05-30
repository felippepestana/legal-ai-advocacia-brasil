from __future__ import annotations

import logging
import os

import requests

from legal_sources.base import SearchHit

logger = logging.getLogger(__name__)

API_BASE = "https://jurisprudencias.ai/api/v1"

COURT_MAP = {
    "stj": "stj",
    "stf": "stf",
    "tjsp": "tjsp",
    "tjrj": "tjrj",
    "tjmg": "tjmg",
    "trf3": "trf3",
}


def _token() -> str | None:
    token = os.environ.get("JURISPRUDENCIAS_API_TOKEN", "").strip()
    return token or None


def search_jurisprudencias(
    query: str,
    *,
    courts: list[str] | None = None,
    page: int = 0,
    timeout: int = 20,
) -> tuple[list[SearchHit], list[str]]:
    """
    Jurisprudência com texto de acórdãos (STJ, STF, TJs…).
    Requer JURISPRUDENCIAS_API_TOKEN — plano gratuito em jurisprudencias.ai.
    """
    warnings: list[str] = []
    hits: list[SearchHit] = []

    token = _token()
    if not token:
        warnings.append(
            "STJ/jurisprudência textual: configure JURISPRUDENCIAS_API_TOKEN "
            "(ou use DataJud para metadados processuais)."
        )
        return hits, warnings

    court_list = courts or ["stj"]
    headers = {"Authorization": f"Bearer {token}"}

    for court in court_list[:2]:
        court_id = COURT_MAP.get(court.lower(), court.lower())
        url = f"{API_BASE}/courts/{court_id}/decisions"
        try:
            response = requests.get(
                url,
                params={"q": query, "page": page},
                headers=headers,
                timeout=timeout,
            )
            if response.status_code == 401:
                warnings.append("Jurisprudências.ai: token inválido.")
                break
            if response.status_code >= 400:
                warnings.append(f"Jurisprudências.ai ({court_id}): HTTP {response.status_code}")
                continue
            data = response.json()
            items = data if isinstance(data, list) else data.get("decisions") or data.get("items") or []
            for item in items[:8]:
                hit = _hit_from_decision(item, court_id)
                if hit:
                    hits.append(hit)
        except requests.RequestException as exc:
            logger.warning("Jurisprudências.ai: %s", exc)
            warnings.append(f"Jurisprudências.ai: indisponível ({exc.__class__.__name__})")

    return hits, warnings


def _hit_from_decision(item: dict, court_id: str) -> SearchHit | None:
    if not item:
        return None
    numero = item.get("process_number") or item.get("numero") or item.get("number") or ""
    ementa = item.get("ementa") or item.get("snippet") or item.get("summary") or ""
    relator = item.get("relator") or item.get("rapporteur") or ""
    title_parts = [court_id.upper()]
    if numero:
        title_parts.append(str(numero))
    title = " — ".join(title_parts)
    content = ementa
    if relator:
        content = f"Relator(a): {relator}. {content}"
    url = item.get("url") or item.get("link")
    return SearchHit(
        id=f"juris_{court_id}_{numero or hash(ementa) % 10**8}",
        title=title,
        content=content[:3000] or "Sem ementa disponível na API.",
        source=f"Jurisprudências.ai ({court_id.upper()})",
        provider="jurisprudencias",
        court=court_id.upper(),
        url=url,
        relevance_score=0.9,
        metadata={"raw": {k: v for k, v in item.items() if k not in ("text", "full_text")}},
    )
