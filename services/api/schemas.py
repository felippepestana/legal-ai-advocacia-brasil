from datetime import date
from typing import Any

from pydantic import BaseModel, Field


class AnalyzeDocumentRequest(BaseModel):
    text: str = Field(..., min_length=20, description="Texto integral ou trecho do documento")
    legal_area: str | None = Field(None, description="ID da área em ontology/areas-direito.yaml")
    enhance_with_gemini: bool = Field(
        False,
        description="Segunda passagem com Gemini (requer GEMINI_API_KEY no servidor)",
    )


class ValidateDocumentRequest(BaseModel):
    text: str = Field(..., min_length=20)
    tipo_peca: str = Field("peticao_inicial", description="ID em ontology/tipos-documento.yaml")


class CalculateDeadlineRequest(BaseModel):
    event_date: date
    deadline_type: str = Field(..., examples=["contestacao", "recurso"])
    court_type: str = Field("estadual", examples=["estadual", "trabalhista", "federal"])
    custom_days: int | None = None


class CalculateLegalRequest(BaseModel):
    area: str = Field(..., examples=["trabalhista", "civil"])
    subtype: str = Field(..., examples=["rescisao", "danos_morais"])
    parameters: dict[str, Any]


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=3)
    search_type: str = Field("mista", examples=["jurisprudencia", "legislacao", "mista"])
    filters: dict[str, Any] = Field(default_factory=dict)
    synthesize_with_gemini: bool = Field(
        False,
        description="Síntese com Gemini sobre resultados locais (requer GEMINI_API_KEY)",
    )
    use_external_sources: bool = Field(
        True,
        description="Consultar DataJud, Senado/LexML e jurisprudências.ai (se configurado)",
    )
    tribunals: list[str] = Field(
        default_factory=list,
        description="Siglas DataJud (ex.: stj, stf, tjsp). Vazio = padrão STJ+STF+TJSP",
    )


class GenerateDocumentRequest(BaseModel):
    template_id: str = Field(..., examples=["peticao_inicial_civil", "procuracao"])
    data: dict[str, Any]
    ai_enhancement: bool = Field(
        False,
        description="Enriquecimento com Gemini via prompt sistema-geracao-peca",
    )


class CreateWorkflowRequest(BaseModel):
    template_id: str = Field(..., examples=["peticao_inicial", "acompanhamento_prazo"])
    name: str = Field(..., min_length=3)
    variables: dict[str, Any] = Field(default_factory=dict)


class ExecuteWorkflowRequest(BaseModel):
    workflow_id: str
    context: dict[str, Any] = Field(default_factory=dict)


class AssistantChatRequest(BaseModel):
    message: str = Field(..., min_length=2)
    user_level: str = Field("advogado", examples=["advogado", "estagiario", "cliente"])
    enhance_with_gemini: bool = Field(False)


class AnalyticsRunRequest(BaseModel):
    analysis_type: str = Field(
        "performance",
        examples=["performance", "predictive", "financial"],
    )
    num_cases: int = Field(500, ge=50, le=2000)
    export_charts: bool = Field(
        False,
        description="Gera gráficos PNG em data/analytics/charts (ou ANALYTICS_CHARTS_DIR)",
    )


class HealthResponse(BaseModel):
    status: str
    version: str
    hub: str
    gemini_available: bool = False
    ai_backend: str | None = Field(None, description="api_key | vertex")
    ai_model: str | None = None
    ai_project: str | None = Field(None, description="Projeto GCP quando backend=vertex")
    ai_location: str | None = None
    auth_required: bool = False
    tenants_configured: int = 0
    rate_limit_enabled: bool = False
    rate_limit_requests: int | None = None
    rate_limit_window_seconds: int | None = None
    sentry_enabled: bool = False
    structured_logging: bool = False
    slack_alerts_enabled: bool = False
    redis_enabled: bool = False
    redis_connected: bool = False
    rate_limit_backend: str | None = Field(None, description="redis | memory | memory_fallback")
    search_cache_backend: str | None = None
