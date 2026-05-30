"""Testes de rate limiting por tenant."""

import json

import pytest
from fastapi.testclient import TestClient

import services.api.bootstrap  # noqa: F401

from services.api.main import app
from services.api.rate_limit import reset_buckets


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_rate_limits():
    reset_buckets()
    yield
    reset_buckets()


@pytest.fixture(autouse=True)
def clear_env(monkeypatch):
    for key in ("TENANTS_JSON", "TENANT_KEYS_PATH", "AUTH_REQUIRED", "RATE_LIMIT_ENABLED"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("RATE_LIMIT_ENABLED", "true")
    monkeypatch.setenv("RATE_LIMIT_REQUESTS", "3")
    monkeypatch.setenv("RATE_LIMIT_WINDOW_SECONDS", "60")


def _search(client, headers=None):
    return client.post(
        "/v1/search/query",
        headers=headers or {},
        json={"query": "danos morais consumidor", "use_external_sources": False},
    )


def test_rate_limit_blocks_anonymous_ip(client):
    for _ in range(3):
        assert _search(client).status_code == 200
    blocked = _search(client)
    assert blocked.status_code == 429
    assert "retry_after_seconds" in blocked.json()


def test_rate_limit_isolated_per_tenant(client, monkeypatch):
    tenants = [
        {"tenant_id": "t1", "name": "T1", "api_key": "key-a", "rate_limit_rpm": 2},
        {"tenant_id": "t2", "name": "T2", "api_key": "key-b", "rate_limit_rpm": 2},
    ]
    monkeypatch.setenv("TENANTS_JSON", json.dumps(tenants))
    monkeypatch.setenv("AUTH_REQUIRED", "true")
    monkeypatch.setenv("RATE_LIMIT_REQUESTS", "100")

    assert _search(client, {"X-API-Key": "key-a"}).status_code == 200
    assert _search(client, {"X-API-Key": "key-a"}).status_code == 200
    assert _search(client, {"X-API-Key": "key-a"}).status_code == 429
    assert _search(client, {"X-API-Key": "key-b"}).status_code == 200
