from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Any

from legal_sources.base import SearchHit
from legal_sources.datajud import search_datajud
from legal_sources.jurisprudencias import search_jurisprudencias
from legal_sources.lexml import search_lexml_sru
from legal_sources.senado_legislacao import search_senado_legislacao

logger = logging.getLogger(__name__)


def _dedupe_hits(hits: list[SearchHit]) -> list[SearchHit]:
    seen: set[str] = set()
    unique: list[SearchHit] = []
    for hit in hits:
        key = hit.id or hit.title
        if key in seen:
            continue
        seen.add(key)
        unique.append(hit)
    return unique


def _serialize_for_cache(payload: dict[str, Any]) -> dict[str, Any]:
    hits = payload.get("hits", [])
    return {
        **payload,
        "hits": [h.to_dict() if isinstance(h, SearchHit) else h for h in hits],
    }


def _hit_from_dict(raw: dict[str, Any]) -> SearchHit:
    date = None
    if raw.get("date"):
        try:
            date = datetime.fromisoformat(str(raw["date"]))
        except ValueError:
            date = None
    meta = dict(raw.get("metadata") or {})
    provider = meta.pop("provider", raw.get("source", ""))
    return SearchHit(
        id=str(raw.get("id", "")),
        title=str(raw.get("title", "")),
        content=str(raw.get("content", "")),
        source=str(raw.get("source", "")),
        provider=str(provider),
        court=raw.get("court"),
        date=date,
        url=raw.get("url"),
        relevance_score=float(raw.get("relevance_score", 0.5)),
        metadata=meta,
    )


def _deserialize_cached(payload: dict[str, Any]) -> dict[str, Any]:
    hits_raw = payload.get("hits", [])
    hits = [_hit_from_dict(h) if isinstance(h, dict) else h for h in hits_raw]
    return {**payload, "hits": hits}


def search_external_sources(
    query: str,
    search_type: str = "mista",
    *,
    tribunals: list[str] | None = None,
    use_datajud: bool = True,
    use_legislation: bool = True,
    use_jurisprudencias: bool = True,
) -> dict[str, Any]:
    """
    Agrega fontes públicas conforme o tipo de pesquisa.
    """
    from legal_sources.cache import get_cached, make_cache_key, set_cached

    cache_key = make_cache_key(
        query,
        search_type,
        tribunals,
        use_datajud=use_datajud,
        use_legislation=use_legislation,
        use_jurisprudencias=use_jurisprudencias,
    )
    cached = get_cached(cache_key)
    if cached is not None:
        return _deserialize_cached(cached)

    st = search_type.lower()
    all_hits: list[SearchHit] = []
    warnings: list[str] = []
    providers_used: list[str] = []

    if st in ("jurisprudencia", "mista", "casos", "precedentes") and use_datajud:
        dj_hits, dj_warn = search_datajud(query, tribunals=tribunals)
        all_hits.extend(dj_hits)
        warnings.extend(dj_warn)
        if dj_hits:
            providers_used.append("datajud")

    if st in ("jurisprudencia", "mista", "precedentes") and use_jurisprudencias:
        courts = tribunals or ["stj"]
        j_hits, j_warn = search_jurisprudencias(query, courts=courts)
        all_hits.extend(j_hits)
        warnings.extend(j_warn)
        if j_hits:
            providers_used.append("jurisprudencias")

    if st in ("legislacao", "mista"):
        if use_legislation:
            lexml_hits, lexml_warn = search_lexml_sru(query)
            warnings.extend(lexml_warn)
            if lexml_hits:
                all_hits.extend(lexml_hits)
                providers_used.append("lexml")

            sen_hits, sen_warn = search_senado_legislacao(query)
            all_hits.extend(sen_hits)
            warnings.extend(sen_warn)
            if sen_hits:
                providers_used.append("senado_legislacao")

    all_hits = _dedupe_hits(all_hits)
    all_hits.sort(key=lambda h: h.relevance_score, reverse=True)

    result = {
        "hits": all_hits,
        "warnings": warnings,
        "providers_used": providers_used,
        "cache_hit": False,
    }
    set_cached(cache_key, _serialize_for_cache(result))
    return result
