# Guia de deploy — Legal AI Platform

## Desenvolvimento local

Pasta recomendada: **`D:\DEV\LEGA-AI`**

```powershell
cd D:\DEV\LEGA-AI
.\scripts\setup_dev.ps1
.\scripts\run_dev.ps1
```

| Serviço | URL |
|---------|-----|
| API | http://127.0.0.1:8000/docs |
| Web (Vite) | http://localhost:5173 |

## Stack Docker (API + Web + Redis)

```powershell
cd D:\DEV\LEGA-AI
docker compose up --build
```

| Serviço | URL |
|---------|-----|
| Web (nginx) | http://localhost:8080 |
| API direta | http://localhost:8000/docs |
| Redis | localhost:6379 |

O frontend em Docker faz proxy de `/v1` para o container `api`.

### Variáveis para produção local via `.env`

Crie `.env` na raiz e referencie no `docker-compose` (extensão futura) ou exporte antes do `docker compose up`:

```env
GEMINI_API_KEY=sua-chave
AUTH_REQUIRED=true
TENANT_KEYS_PATH=config/tenants.json
SENTRY_DSN=
SLACK_WEBHOOK_URL=
```

## Cloud Run (API)

Pré-requisitos GCP:

1. API Vertex AI habilitada
2. Service account com `roles/aiplatform.user`
3. (Opcional) Memorystore Redis + `REDIS_URL`

```powershell
gcloud builds submit --tag gcr.io/SEU_PROJETO/advocacia-api
gcloud run deploy advocacia-api `
  --image gcr.io/SEU_PROJETO/advocacia-api `
  --region us-central1 `
  --set-env-vars "AI_BACKEND=vertex,GOOGLE_CLOUD_PROJECT=SEU_PROJETO,VERTEX_LOCATION=us-central1,REDIS_URL=redis://...,RATE_LIMIT_ENABLED=true,LOG_FORMAT=json"
```

Deploy automatizado: GitHub Actions → `.github/workflows/deploy-cloud-run.yml` (manual dispatch).

## Frontend estático

Build:

```powershell
cd apps\web
npm run build
```

Sirva `apps/web/dist` via Firebase Hosting, Cloud Storage + CDN, ou nginx (ver `apps/web/Dockerfile`).

Configure a URL da API no proxy reverso (`/v1` → Cloud Run) ou ajuste `apps/web/src/api/client.js` para URL absoluta em produção.

## Checklist pós-deploy

- [ ] `GET /v1/health` retorna `status: ok`
- [ ] `gemini_available: true` ou Vertex configurado
- [ ] `redis_connected: true` (se multi-instância)
- [ ] Auth com tenants de produção (nunca usar keys de demo)
- [ ] Sentry e Slack webhook testados
- [ ] Export CSV de auditoria acessível para compliance
