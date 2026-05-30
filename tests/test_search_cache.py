"""Testes de cache de pesquisa externa."""

import services.api.bootstrap  # noqa: F401

from legal_sources.aggregator import search_external_sources


def test_external_search_cache_hit(monkeypatch):
    from legal_sources import cache as cache_mod

    cache_mod.clear_cache()
    calls = {"count": 0}

    def fake_datajud(query, tribunals=None):
        calls["count"] += 1
        from legal_sources.base import SearchHit

        return (
            [
                SearchHit(
                    id="hit-1",
                    title="Acórdão teste",
                    content="Ementa de teste",
                    source="STJ",
                    provider="datajud",
                    relevance_score=0.9,
                )
            ],
            [],
        )

    monkeypatch.setenv("SEARCH_CACHE_ENABLED", "true")
    monkeypatch.setenv("SEARCH_CACHE_TTL_SECONDS", "3600")
    monkeypatch.setattr("legal_sources.aggregator.search_datajud", fake_datajud)
    monkeypatch.setattr("legal_sources.aggregator.search_jurisprudencias", lambda *a, **k: ([], []))
    monkeypatch.setattr("legal_sources.aggregator.search_lexml_sru", lambda *a, **k: ([], []))
    monkeypatch.setattr("legal_sources.aggregator.search_senado_legislacao", lambda *a, **k: ([], []))

    first = search_external_sources("danos morais", "jurisprudencia", tribunals=["stj"])
    second = search_external_sources("danos morais", "jurisprudencia", tribunals=["stj"])

    assert calls["count"] == 1
    assert first["cache_hit"] is False
    assert second["cache_hit"] is True
    assert len(second["hits"]) == 1
