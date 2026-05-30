"""Testes de auditoria IA."""

import json

import pytest

import services.api.bootstrap  # noqa: F401

from ai_provider.client import generate_content
from ai_provider.config import AIConfig
from ai_provider.context import bind_ai_context, reset_ai_context
from services.api.audit_store import log_ai_event, read_recent_events


@pytest.fixture(autouse=True)
def audit_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("AUDIT_LOG_DIR", str(tmp_path / "audit"))
    monkeypatch.setenv("AI_AUDIT_ENABLED", "true")
    yield


def test_log_ai_event_writes_jsonl():
    log_ai_event(
        tenant_id="t1",
        operation="test_op",
        model="gemini-2.0-flash",
        backend="api_key",
        system_prompt="system",
        user_prompt="user prompt",
        latency_ms=42,
        success=True,
        output_chars=100,
    )
    events = read_recent_events()
    assert len(events) == 1
    assert events[0]["tenant_id"] == "t1"
    assert events[0]["operation"] == "test_op"
    assert "prompt_hash" in events[0]
    assert "user prompt" not in json.dumps(events[0])


def test_generate_content_audits_on_failure(monkeypatch):
    cfg = AIConfig(backend="api_key", model="gemini-2.0-flash", api_key="x")

    def boom(*args, **kwargs):
        raise RuntimeError("falha simulada")

    monkeypatch.setattr("ai_provider.client._generate_with_genai", boom)
    monkeypatch.setattr("ai_provider.client._generate_with_legacy_sdk", boom)

    tokens = bind_ai_context(tenant_id="tenant-x", operation="unit_test")
    try:
        with pytest.raises(RuntimeError):
            generate_content(cfg, "sys", "usr", operation="unit_test")
    finally:
        reset_ai_context(tokens)

    events = read_recent_events()
    assert events[-1]["success"] is False
    assert events[-1]["tenant_id"] == "tenant-x"
