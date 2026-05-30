import services.api.bootstrap  # noqa: F401 — sys.path

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from services.api.config import API_PREFIX, CORS_ORIGINS
from services.api.middleware import RateLimitMiddleware, TenantAuthMiddleware
from services.api.observability import setup_observability
from services.api.routes import api_router
from services.api.version import APP_VERSION


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_observability(app)
    yield


app = FastAPI(
    title="Legal AI Platform — Advocacia Brasil",
    description="API unificada: análise documental, validação CPC, prazos e cálculos.",
    version=APP_VERSION,
    lifespan=lifespan,
)

app.add_middleware(RateLimitMiddleware)
app.add_middleware(TenantAuthMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=API_PREFIX)


@app.get("/")
def root() -> dict:
    return {
        "message": "Legal AI Platform API",
        "docs": "/docs",
        "health": f"{API_PREFIX}/health",
    }
