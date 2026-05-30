"""Configura sys.path: modules canônicos, raiz legada e packages/."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODULES_ROOT = PROJECT_ROOT / "services" / "modules"
PACKAGES_ROOT = PROJECT_ROOT / "packages"

# insert(0) empilha — iterar do menos ao mais prioritário
for path in (str(PACKAGES_ROOT), str(PROJECT_ROOT), str(MODULES_ROOT)):
    if path not in sys.path:
        sys.path.insert(0, path)
