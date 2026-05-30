"""Testes de configuração IA (sem chamadas à API real)."""

import os

import pytest

import services.api.bootstrap  # noqa: F401

from ai_provider.config import AIConfig, get_ai_status


@pytest.fixture(autouse=True)
def clear_ai_env(monkeypatch):
    for key in (
        "GEMINI_API_KEY",
        "GOOGLE_API_KEY",
        "GOOGLE_CLOUD_PROJECT",
        "VERTEX_LOCATION",
        "AI_BACKEND",
        "GEMINI_MODEL",
    ):
        monkeypatch.delenv(key, raising=False)


def test_ai_unavailable_without_credentials():
    assert AIConfig.from_env() is None
    status = get_ai_status()
    assert status["available"] is False


def test_ai_api_key_backend():
    os.environ["GEMINI_API_KEY"] = "test-key"
    os.environ["AI_BACKEND"] = "api_key"
    cfg = AIConfig.from_env()
    assert cfg is not None
    assert cfg.backend == "api_key"
    assert cfg.api_key == "test-key"
    assert cfg.model == "gemini-2.0-flash"


def test_ai_vertex_backend_requires_project():
    os.environ["AI_BACKEND"] = "vertex"
    assert AIConfig.from_env() is None

    os.environ["GOOGLE_CLOUD_PROJECT"] = "meu-projeto"
    os.environ["VERTEX_LOCATION"] = "southamerica-east1"
    cfg = AIConfig.from_env()
    assert cfg is not None
    assert cfg.backend == "vertex"
    assert cfg.project == "meu-projeto"
    assert cfg.location == "southamerica-east1"


def test_ai_auto_prefers_api_key_when_both_set():
    os.environ["GEMINI_API_KEY"] = "dev-key"
    os.environ["GOOGLE_CLOUD_PROJECT"] = "prod-project"
    cfg = AIConfig.from_env()
    assert cfg is not None
    assert cfg.backend == "api_key"


def test_ai_auto_vertex_when_only_project():
    os.environ["GOOGLE_CLOUD_PROJECT"] = "prod-project"
    cfg = AIConfig.from_env()
    assert cfg is not None
    assert cfg.backend == "vertex"


def test_get_ai_status_vertex():
    os.environ["AI_BACKEND"] = "vertex"
    os.environ["GOOGLE_CLOUD_PROJECT"] = "advocacia-prod"
    status = get_ai_status()
    assert status["available"] is True
    assert status["backend"] == "vertex"
    assert status["project"] == "advocacia-prod"
