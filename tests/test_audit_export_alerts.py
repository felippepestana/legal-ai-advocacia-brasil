"""Testes de export CSV e alertas Slack."""

import csv
import io

import pytest
from fastapi.testclient import TestClient

import services.api.bootstrap  # noqa: F401

from services.api.audit_store import events_to_csv, log_ai_event
from services.api.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_events_to_csv_format():
    events = [
        {
            "ts": "2026-05-27T12:00:00+00:00",
            "tenant_id": "t1",
            "operation": "assistant_chat",
            "model": "gemini-2.0-flash",
            "backend": "api_key",
            "latency_ms": 120,
            "prompt_hash": "abc123",
            "system_chars": 10,
            "user_chars": 20,
            "output_chars": 100,
            "success": True,
        }
    ]
    csv_text = events_to_csv(events)
    rows = list(csv.DictReader(io.StringIO(csv_text)))
    assert len(rows) == 1
    assert rows[0]["tenant_id"] == "t1"
    assert rows[0]["success"] == "true"


def test_audit_export_csv_endpoint(client, tmp_path, monkeypatch):
    monkeypatch.setenv("AUDIT_LOG_DIR", str(tmp_path))
    log_ai_event(
        tenant_id="public",
        operation="unit_test",
        model="gemini-2.0-flash",
        backend="api_key",
        system_prompt="sys",
        user_prompt="usr",
        latency_ms=10,
        success=True,
        output_chars=5,
    )

    response = client.get("/v1/audit/export?limit=10")
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    assert "attachment" in response.headers.get("content-disposition", "")
    rows = list(csv.DictReader(io.StringIO(response.text)))
    assert len(rows) >= 1
    assert rows[0]["operation"] == "unit_test"


def test_slack_notify_on_ai_failure(tmp_path, monkeypatch):
    monkeypatch.setenv("AUDIT_LOG_DIR", str(tmp_path))
    monkeypatch.setenv("SLACK_WEBHOOK_URL", "https://hooks.slack.com/services/test")
    calls = []

    def fake_post(url, json, timeout):
        calls.append({"url": url, "json": json, "timeout": timeout})

        class Resp:
            status_code = 200

            def raise_for_status(self):
                return None

        return Resp()

    monkeypatch.setattr("services.api.alerts.requests.post", fake_post)

    log_ai_event(
        tenant_id="escritorio-a",
        operation="document_enhance",
        model="gemini-2.0-flash",
        backend="vertex",
        system_prompt="system",
        user_prompt="user",
        latency_ms=50,
        success=False,
        error="quota exceeded",
        output_chars=0,
    )

    assert len(calls) == 1
    assert "Falha em consulta IA" in calls[0]["json"]["text"]


def test_slack_skipped_when_disabled(tmp_path, monkeypatch):
    monkeypatch.setenv("AUDIT_LOG_DIR", str(tmp_path))
    monkeypatch.setenv("SLACK_ALERTS_ENABLED", "false")
    monkeypatch.setenv("SLACK_WEBHOOK_URL", "https://hooks.slack.com/services/test")

    def fail_post(*args, **kwargs):
        raise AssertionError("Slack não deveria ser chamado")

    monkeypatch.setattr("services.api.alerts.requests.post", fail_post)

    log_ai_event(
        tenant_id="t1",
        operation="test",
        model="m",
        backend="api_key",
        system_prompt="s",
        user_prompt="u",
        latency_ms=1,
        success=False,
        error="x",
    )
