from pathlib import Path

from legal_core.paths import PROMPTS_DIR


def load_prompt(name: str) -> str:
    """Carrega prompt por nome de arquivo sem extensão (ex.: sistema-analise-documento)."""
    path = PROMPTS_DIR / f"{name}.md"
    if not path.is_file():
        raise FileNotFoundError(f"Prompt não encontrado: {path}")
    return path.read_text(encoding="utf-8")


def list_prompts() -> list[str]:
    return sorted(p.stem for p in PROMPTS_DIR.glob("sistema-*.md"))
