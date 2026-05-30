"""Testes de autenticação multi-tenant."""

import json

import pytest
from fastapi.testclient import TestClient

import services.api.bootstrap  # noqa: F401

from services.api.main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def clear_auth_env(monkeypatch):
    for key in ("TENANTS_JSON", "TENANT_KEYS_PATH", "AUTH_REQUIRED"):
        monkeypatch.delenv(key, raising=False)


def test_public_health_without_auth(client):
    response = client.get("/v1/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["auth_required"] is False


def test_auth_required_blocks_anonymous(client, monkeypatch):
    tenants = [{"tenant_id": "t1", "name": "T1", "api_key": "secret-key"}]
    monkeypatch.setenv("TENANTS_JSON", json.dumps(tenants))
    monkeypatch.setenv("AUTH_REQUIRED", "true")

    response = client.post(
        "/v1/search/query",
        json={"query": "danos morais", "use_external_sources": False},
    )
    assert response.status_code == 401


def test_valid_api_key_allows_request(client, monkeypatch):
    tenants = [{"tenant_id": "t1", "name": "T1", "api_key": "secret-key"}]
    monkeypatch.setenv("TENANTS_JSON", json.dumps(tenants))
    monkeypatch.setenv("AUTH_REQUIRED", "true")

    response = client.post(
        "/v1/search/query",
        headers={"X-API-Key": "secret-key"},
        json={"query": "danos morais consumidor", "use_external_sources": False},
    )
    assert response.status_code == 200
    assert response.json()["total_results"] >= 1
