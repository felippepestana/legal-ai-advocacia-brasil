from fastapi import APIRouter

from services.api.routes import (
    analytics,
    assistant,
    calculator,
    deadlines,
    documents,
    generation,
    meta,
    search,
    workflows,
)

api_router = APIRouter()
api_router.include_router(meta.router, tags=["meta"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(deadlines.router, prefix="/deadlines", tags=["deadlines"])
api_router.include_router(calculator.router, prefix="/calculator", tags=["calculator"])
api_router.include_router(search.router, prefix="/search", tags=["search"])
api_router.include_router(generation.router, prefix="/generation", tags=["generation"])
api_router.include_router(workflows.router, prefix="/workflows", tags=["workflows"])
api_router.include_router(assistant.router, prefix="/assistant", tags=["assistant"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
