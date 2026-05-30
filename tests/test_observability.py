"""Testes de observabilidade (Sentry / logging estruturado)."""

import json

import pytest
from fastapi.testclient import TestClient

import services.api.bootstrap  # noqa: F401

from services.api.main import app


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_health_includes_monitoring_flags(monkeypatch):
    monkeypatch.delenv("SENTRY_DSN", raising=False)
    monkeypatch.setenv("LOG_FORMAT", "json")

    with TestClient(app) as client:
        response = client.get("/v1/health")
        assert response.status_code == 200
        body = response.json()
        assert body["sentry_enabled"] is False
        assert body["structured_logging"] is True


def test_sentry_enabled_when_dsn_set(client, monkeypatch):
    monkeypatch.setenv("SENTRY_DSN", "https://example@sentry.io/1")
    monkeypatch.setenv("LOG_FORMAT", "text")

    try:
        import sentry_sdk
    except ImportError:
        pytest.skip("sentry-sdk não instalado")

    with TestClient(app) as fresh_client:
        response = fresh_client.get("/v1/health")
        assert response.status_code == 200
        assert response.json()["sentry_enabled"] is True


def test_structured_log_format(monkeypatch):
    monkeypatch.setenv("LOG_FORMAT", "json")
    from services.api.observability import JsonLogFormatter
    import logging

    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="evento de teste",
        args=(),
        exc_info=None,
    )
    payload = json.loads(JsonLogFormatter().format(record))
    assert payload["message"] == "evento de teste"
    assert payload["severity"] == "INFO"
