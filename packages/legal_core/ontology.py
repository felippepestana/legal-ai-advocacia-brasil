from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from legal_core.paths import ONTOLOGY_DIR


@lru_cache(maxsize=8)
def load_ontology(filename: str) -> dict[str, Any]:
    path = ONTOLOGY_DIR / filename
    if not path.is_file():
        raise FileNotFoundError(f"Ontologia não encontrada: {path}")
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def document_type_ids() -> list[str]:
    data = load_ontology("tipos-documento.yaml")
    return [t["id"] for t in data.get("tipos", [])]


def legal_area_ids() -> list[str]:
    data = load_ontology("areas-direito.yaml")
    return [a["id"] for a in data.get("areas", [])]
