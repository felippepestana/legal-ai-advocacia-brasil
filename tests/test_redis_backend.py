"""Testes de backend Redis (rate limit + cache)."""

import json

import fakeredis
import pytest
from fastapi.testclient import TestClient

import services.api.bootstrap  # noqa: F401

from infra import redis as redis_mod
from legal_sources.aggregator import search_external_sources
from legal_sources import cache as cache_mod
from services.api.main import app
from services.api.rate_limit import reset_buckets


@pytest.fixture
def fake_redis(monkeypatch):
    server = fakeredis.FakeStrictRedis(decode_responses=True)
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
    redis_mod.reset_client()
    monkeypatch.setattr(redis_mod, "_client", server)
    monkeypatch.setattr(redis_mod, "_client_checked", True)
    yield server
    redis_mod.reset_client()


@pytest.fixture
def client():
    return TestClient(app)


def test_redis_search_cache_hit(fake_redis, monkeypatch):
    cache_mod.clear_cache()
    calls = {"count": 0}

    def fake_datajud(query, tribunals=None):
        calls["count"] += 1
        from legal_sources.base import SearchHit

        return (
            [
                SearchHit(
                    id="hit-redis",
                    title="Acórdão redis",
                    content="Ementa",
                    source="STJ",
                    provider="datajud",
                    relevance_score=0.9,
                )
            ],
            [],
        )

    monkeypatch.setenv("SEARCH_CACHE_ENABLED", "true")
    monkeypatch.setattr("legal_sources.aggregator.search_datajud", fake_datajud)
    monkeypatch.setattr("legal_sources.aggregator.search_jurisprudencias", lambda *a, **k: ([], []))
    monkeypatch.setattr("legal_sources.aggregator.search_lexml_sru", lambda *a, **k: ([], []))
    monkeypatch.setattr("legal_sources.aggregator.search_senado_legislacao", lambda *a, **k: ([], []))

    first = search_external_sources("redis cache test", "jurisprudencia", tribunals=["stj"])
    cache_mod._MEMORY.clear()
    second = search_external_sources("redis cache test", "jurisprudencia", tribunals=["stj"])

    assert calls["count"] == 1
    assert first["cache_hit"] is False
    assert second["cache_hit"] is True


def test_redis_rate_limit(fake_redis, client, monkeypatch):
    reset_buckets()
    monkeypatch.setenv("RATE_LIMIT_ENABLED", "true")
    monkeypatch.setenv("RATE_LIMIT_REQUESTS", "2")
    monkeypatch.setenv("RATE_LIMIT_WINDOW_SECONDS", "60")

    payload = {"query": "danos morais consumidor", "use_external_sources": False}
    assert client.post("/v1/search/query", json=payload).status_code == 200
    assert client.post("/v1/search/query", json=payload).status_code == 200
    blocked = client.post("/v1/search/query", json=payload)
    assert blocked.status_code == 429


def test_health_exposes_redis(client, fake_redis):
    resp = client.get("/v1/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["redis_enabled"] is True
    assert body["redis_connected"] is True
    assert body["rate_limit_backend"] == "redis"
    assert body["search_cache_backend"] == "redis"
