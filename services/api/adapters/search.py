from __future__ import annotations

from datetime import datetime
from functools import lru_cache
from typing import Any
from uuid import uuid4

import services.api.bootstrap  # noqa: F401

from enhanced_intelligent_search import EnhancedSearchEngine, SearchQuery, SearchType

_SEARCH_TYPE_MAP = {
    "jurisprudencia": SearchType.JURISPRUDENCE,
    "legislacao": SearchType.LEGISLATION,
    "doutrina": SearchType.DOCTRINE,
    "casos": SearchType.CASES,
    "precedentes": SearchType.PRECEDENTS,
    "mista": SearchType.MIXED,
}


@lru_cache(maxsize=1)
def get_engine() -> EnhancedSearchEngine:
    return EnhancedSearchEngine()


def _result_to_dict(result: Any) -> dict[str, Any]:
    return {
        "id": result.id,
        "title": result.title,
        "content": result.content,
        "source": result.source,
        "court": result.court.value if result.court else None,
        "date": result.date.isoformat() if result.date else None,
        "area": result.area.value if result.area else None,
        "relevance_score": float(result.relevance_score),
        "url": result.url,
        "metadata": result.metadata,
    }


def _merge_results(
    local: list[dict[str, Any]],
    external: list[dict[str, Any]],
    *,
    limit: int = 25,
) -> list[dict[str, Any]]:
    seen: set[str] = set()
    merged: list[dict[str, Any]] = []

    for item in external + local:
        key = item.get("id") or item.get("title", "")
        if key in seen:
            continue
        seen.add(key)
        merged.append(item)
        if len(merged) >= limit:
            break

    merged.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
    return merged


def run_search(
    text: str,
    search_type: str = "mista",
    filters: dict[str, Any] | None = None,
    synthesize_with_gemini: bool = False,
    use_external_sources: bool = True,
    tribunals: list[str] | None = None,
    user_id: str = "api",
) -> dict[str, Any]:
    st = _SEARCH_TYPE_MAP.get(search_type.lower(), SearchType.MIXED)
    query = SearchQuery(
        id=str(uuid4()),
        text=text,
        search_type=st,
        filters=filters or {},
        user_id=user_id,
        timestamp=datetime.now(),
    )
    response = get_engine().search(query)
    local_results = [_result_to_dict(r) for r in response.results]

    external_warnings: list[str] = []
    providers_used: list[str] = []
    external_dicts: list[dict[str, Any]] = []
    cache_hit = False

    if use_external_sources:
        from legal_sources.aggregator import search_external_sources

        external = search_external_sources(
            text,
            search_type,
            tribunals=tribunals,
        )
        external_warnings = external.get("warnings", [])
        providers_used = external.get("providers_used", [])
        external_dicts = [h.to_dict() for h in external.get("hits", [])]
        cache_hit = bool(external.get("cache_hit"))

    results = _merge_results(local_results, external_dicts)

    if providers_used:
        disclaimer = (
            "Resultados combinam base local de apoio com fontes públicas "
            f"({', '.join(providers_used)}). Confirme citações nos sites oficiais antes de protocolar."
        )
    else:
        disclaimer = (
            "Base local de apoio; fontes externas indisponíveis ou desativadas. "
            "Confirme em tribunais e LexML/Senado antes de citar."
        )

    payload: dict[str, Any] = {
        "query": text,
        "search_type": search_type,
        "total_results": len(results),
        "search_time_ms": int(response.search_time * 1000),
        "results": results,
        "suggestions": response.suggestions,
        "filters_applied": response.filters_applied,
        "disclaimer": disclaimer,
        "sources": {
            "local_count": len(local_results),
            "external_count": len(external_dicts),
            "providers": providers_used,
            "warnings": external_warnings,
            "cache_hit": cache_hit,
        },
    }

    if synthesize_with_gemini:
        from ai_provider.gemini import is_gemini_available, synthesize_search_results

        if not is_gemini_available():
            raise ValueError("IA não configurada para síntese.")
        payload["synthesis"] = synthesize_search_results(text, results)
        payload["metadata"] = {"ai_enhanced": True}

    return payload
