"""Smoke test da stack Docker (arquivos de compose e Dockerfiles)."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_docker_compose_services():
    text = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    for service in ("redis", "api", "web"):
        assert f"{service}:" in text


def test_api_dockerfile_copies_config():
    dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")
    assert "COPY config/" in dockerfile


def test_web_dockerfile_exists():
    assert (ROOT / "apps" / "web" / "Dockerfile").is_file()
    assert (ROOT / "apps" / "web" / "nginx.conf").is_file()


def test_web_cloudrun_dockerfile_exists():
    assert (ROOT / "apps" / "web" / "Dockerfile.cloudrun").is_file()
    assert (ROOT / "cloudbuild.web.yaml").is_file()
    assert (ROOT / "scripts" / "deploy_gcp.ps1").is_file()
    assert (ROOT / "ops" / "GCP-SETUP.md").is_file()
    assert (ROOT / "ops" / "DEPLOY.md").is_file()
