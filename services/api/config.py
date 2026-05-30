import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
API_PREFIX = os.getenv("API_PREFIX", "/v1")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
LOG_LEVEL = os.getenv("LOG_LEVEL", "info")
