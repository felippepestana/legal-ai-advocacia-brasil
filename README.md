# Plataforma Jurídica V2 — Advocacia Brasil

Plataforma jurídica unificada (ordenamento brasileiro): análise documental, validação CPC, prazos, cálculos, pesquisa, peças, workflows, assistente IA, analytics e auditoria LGPD.

**Versão atual:** 2.0.0 — escopo exclusivamente **jurídico + gestão/administração** (sem verticais odontológicas ou de saúde). Ver `CHANGELOG.md` e `advocacia-brasil-hub/docs/escopo-v2-juridico.md`.

## Estrutura

| Pasta | Conteúdo |
|-------|----------|
| `advocacia-brasil-hub/` | Ontologia, prompts, skills, schemas, documentação |
| `packages/legal_core/` | Validadores, serializers, carregador de prompts |
| `services/api/` | API FastAPI (`/v1`) |
| `apps/web/` | Frontend React (Vite) — consome a API |
| `packages/ai_provider/` | IA Gemini (API key) ou Vertex AI (produção) |
| `services/modules/` | Módulos canônicos Manus (prioridade no import) |
| `legacy/` | Referência ao export original na raiz |
| `*.py` (raiz) | Cópias legadas do export Manus |

## Requisitos

- Python 3.11+
- Node.js 20+ (frontend)
- `pip install -r requirements.txt`

> **Ambiente local recomendado:** `D:\DEV\LEGA-AI` (fora do Google Drive). Veja `LOCAL-DEV.md`.

## Setup rápido

```powershell
cd D:\DEV\LEGA-AI
.\scripts\setup_dev.ps1
```

## Executar API

```powershell
cd D:\DEV\LEGA-AI
python -m uvicorn services.api.main:app --reload --host 0.0.0.0 --port 8000
```

Documentação interativa: http://localhost:8000/docs

## Executar frontend

```powershell
cd apps\web
npm install
npm run dev
```

Interface: http://localhost:5173 (proxy `/v1` → API na porta 8000).

Atalho (API + web): `.\scripts\run_dev.ps1`

## Stack Docker (API + Web + Redis)

```powershell
docker compose up --build
```

Web: http://localhost:8080 — API: http://localhost:8000/docs

Guia completo: `ops/DEPLOY.md`

## Endpoints principais

| Método | Rota | Função |
|--------|------|--------|
| GET | `/v1/health` | Status |
| POST | `/v1/documents/analyze` | Análise documental |
| POST | `/v1/documents/validate` | Validação CPC (petição inicial) |
| POST | `/v1/deadlines/calculate` | Prazo em dias úteis (BR) |
| POST | `/v1/calculator/run` | Cálculo trabalhista/cível |
| POST | `/v1/search/query` | Pesquisa normativa (base local + síntese Gemini opcional) |
| GET | `/v1/generation/templates` | Lista templates de peças |
| POST | `/v1/generation/generate` | Gera minuta a partir de template |
| GET | `/v1/prompts/{name}` | System prompt do hub |

### Exemplo — análise

```json
POST /v1/documents/analyze
{
  "text": "EXCELENTÍSSIMO SENHOR DOUTOR JUIZ... AÇÃO DE COBRANÇA... CPF... valor da causa...",
  "legal_area": "civil"
}
```

### Exemplo — prazo de contestação

```json
POST /v1/deadlines/calculate
{
  "event_date": "2026-05-20",
  "deadline_type": "contestacao",
  "court_type": "estadual"
}
```

## Configuração de IA

### Desenvolvimento (API key)

```env
GEMINI_API_KEY=sua-chave
AI_BACKEND=api_key
GEMINI_MODEL=gemini-2.0-flash
```

### Produção (Vertex AI)

Use service account ou Application Default Credentials no Cloud Run / GCE:

```env
AI_BACKEND=vertex
GOOGLE_CLOUD_PROJECT=seu-projeto-gcp
VERTEX_LOCATION=us-central1
```

Habilite a API **Vertex AI** no projeto GCP e conceda `roles/aiplatform.user` à service account.

A camada `packages/ai_provider/` usa `google-genai` (Vertex) com fallback para `google-generativeai` (API key).

### Deploy Cloud Run (API)

```powershell
gcloud builds submit --tag gcr.io/SEU_PROJETO/advocacia-api
gcloud run deploy advocacia-api `
  --image gcr.io/SEU_PROJETO/advocacia-api `
  --region us-central1 `
  --set-env-vars AI_BACKEND=vertex,GOOGLE_CLOUD_PROJECT=SEU_PROJETO,VERTEX_LOCATION=us-central1
```

### Multi-tenant e auditoria

Cada escritório recebe uma API key (`X-API-Key` ou `Authorization: Bearer`):

```env
AUTH_REQUIRED=true
TENANT_KEYS_PATH=config/tenants.json
```

Modelo em `config/tenants.example.json`. Sem tenants configurados, a API permanece aberta (`tenant_id=public`).

Consultas IA geram audit log JSONL em `data/audit/` (hash do prompt, sem texto integral). Consulta: `GET /v1/audit/recent`.

### Cache de pesquisa externa

```env
SEARCH_CACHE_ENABLED=true
SEARCH_CACHE_TTL_SECONDS=900
```

Respostas de DataJud/Senado são cacheadas; o campo `sources.cache_hit` indica reutilização.

### Rate limiting

```env
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=120
RATE_LIMIT_WINDOW_SECONDS=60
```

Limite por tenant (`rate_limit_rpm` em `config/tenants.json`) ou por IP quando a API está aberta. Resposta `429` com header `Retry-After`.

Com **Redis** (`REDIS_URL`), rate limit e cache de pesquisa são compartilhados entre instâncias (Cloud Run multi-réplica):

```env
REDIS_URL=redis://localhost:6379/0
```

Local: `docker compose up -d redis`

Sem Redis, o fallback é memória (single process) + disco opcional para cache.

## CI/CD

GitHub Actions em `.github/workflows/`:

| Workflow | Gatilho | Função |
|----------|---------|--------|
| `ci.yml` | push / PR | pytest, build Vite, build Docker |
| `deploy-cloud-run.yml` | manual | deploy API no Cloud Run (WIF + secrets GCP) |

Secrets necessários para deploy: `GCP_WORKLOAD_IDENTITY_PROVIDER`, `GCP_SERVICE_ACCOUNT`.

### Monitoramento

**Sentry** (erros e performance):
```env
SENTRY_DSN=https://...@sentry.io/...
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=0.1
```

**Cloud Logging** (Cloud Run): logs JSON no stdout:
```env
LOG_FORMAT=json
LOG_LEVEL=info
```

O health (`GET /v1/health`) expõe `sentry_enabled`, `structured_logging` e `slack_alerts_enabled`.

**Export CSV:** `GET /v1/audit/export?limit=500` ou botão na aba Auditoria.

**Sentry → Slack (nativo):** no painel Sentry, vá em *Settings → Integrations → Slack* e configure alert rules para erros `level:error` e performance degradada. Complementarmente, falhas de IA disparam webhook Slack quando `SLACK_WEBHOOK_URL` está definido.

Consultas prontas para **Cloud Logging / Grafana**: `ops/cloud-logging-queries.md`.

## Hub de conhecimento

Ver `advocacia-brasil-hub/README.md` e `advocacia-brasil-hub/docs/solucao-full-analise-v2.md`.

## Operação em produção

| Recurso | Configuração |
|---------|--------------|
| Multi-instância | `REDIS_URL` + Memorystore ou Redis gerenciado |
| Logs | `LOG_FORMAT=json` → Cloud Logging |
| Erros | `SENTRY_DSN` |
| Alertas IA | `SLACK_WEBHOOK_URL` |
| Compliance | `GET /v1/audit/export` (CSV) |
| CI/CD | `.github/workflows/ci.yml`, `deploy-cloud-run.yml` |
