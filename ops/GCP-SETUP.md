# Configuração GCP para deploy — Legal AI Platform

Guia passo a passo para publicar API + Web no **Cloud Run** com **Vertex AI**.

## 1. Criar projeto e habilitar APIs

```powershell
gcloud projects create SEU_PROJETO_ID --name="Legal AI"
gcloud config set project SEU_PROJETO_ID

gcloud services enable `
  run.googleapis.com `
  cloudbuild.googleapis.com `
  artifactregistry.googleapis.com `
  aiplatform.googleapis.com `
  secretmanager.googleapis.com `
  iamcredentials.googleapis.com
```

## 2. Vertex AI

No [Console GCP → Vertex AI](https://console.cloud.google.com/vertex-ai), aceite os termos se solicitado.

A service account padrão do Cloud Run precisa de:

```powershell
$PROJECT = "SEU_PROJETO_ID"
$PROJECT_NUMBER = (gcloud projects describe $PROJECT --format="value(projectNumber)")
$SA = "$PROJECT_NUMBER-compute@developer.gserviceaccount.com"

gcloud projects add-iam-policy-binding $PROJECT `
  --member="serviceAccount:$SA" `
  --role="roles/aiplatform.user"
```

## 3. Tenants (multi-tenant) via Secret Manager

```powershell
# Edite config/tenants.json com keys de PRODUÇÃO (nunca use dev-demo-key)
gcloud secrets create tenants-json --data-file=config/tenants.json

gcloud secrets add-iam-policy-binding tenants-json `
  --member="serviceAccount:$SA" `
  --role="roles/secretmanager.secretAccessor"
```

No Cloud Run, mapeie: `TENANTS_JSON` ← secret `tenants-json`.

## 4. Deploy manual (rápido)

```powershell
cd D:\DEV\LEGA-AI
gcloud auth login
gcloud config set project SEU_PROJETO_ID

.\scripts\deploy_gcp.ps1 -ProjectId SEU_PROJETO_ID -Region southamerica-east1
```

Após o deploy:

1. Abra **Cloud Run → advocacia-api → Edit & deploy**
2. Adicione secret `TENANTS_JSON` → `tenants-json:latest`
3. Defina `CORS_ORIGINS` = URL do serviço `advocacia-web`
4. (Opcional) `SENTRY_DSN`, `SLACK_WEBHOOK_URL`, `REDIS_URL`

Validação:

```powershell
curl https://advocacia-api-xxxxx.run.app/v1/health
```

## 5. Deploy via GitHub Actions (CI/CD)

### 5.1 Workload Identity Federation

Execute no Cloud Shell ou com `gcloud` autenticado:

```bash
PROJECT_ID="SEU_PROJETO_ID"
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
POOL_ID="github-pool"
PROVIDER_ID="github-provider"
SA_NAME="github-deploy"
SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
REPO="felippepestana/legal-ai-advocacia-brasil"

gcloud iam service-accounts create $SA_NAME --display-name="GitHub Deploy"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/cloudbuild.builds.editor"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/storage.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/iam.serviceAccountUser"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/secretmanager.secretAccessor"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/artifactregistry.reader"

# Cloud Run precisa puxar imagens do GCR/Artifact Registry no deploy
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:service-${PROJECT_NUMBER}@serverless-robot-prod.iam.gserviceaccount.com" \
  --role="roles/artifactregistry.reader"

gcloud iam workload-identity-pools create $POOL_ID \
  --location=global \
  --display-name="GitHub Pool"

gcloud iam workload-identity-pools providers create-oidc $PROVIDER_ID \
  --location=global \
  --workload-identity-pool=$POOL_ID \
  --display-name="GitHub Provider" \
  --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository" \
  --issuer-uri="https://token.actions.githubusercontent.com"

gcloud iam service-accounts add-iam-policy-binding $SA_EMAIL \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/${POOL_ID}/attribute.repository/${REPO}"

gcloud iam service-accounts add-iam-policy-binding $SA_EMAIL \
  --role="roles/iam.serviceAccountTokenCreator" \
  --member="principalSet://iam.googleapis.com/projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/${POOL_ID}/attribute.repository/${REPO}"
```

Anote o provider (para secret do GitHub):

```
projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/github-pool/providers/github-provider
```

### 5.2 Secrets no GitHub

Repositório → **Settings → Secrets and variables → Actions**:

| Secret | Valor |
|--------|--------|
| `GCP_WORKLOAD_IDENTITY_PROVIDER` | Provider WIF (acima) |
| `GCP_SERVICE_ACCOUNT` | `github-deploy@SEU_PROJETO.iam.gserviceaccount.com` |
| `GCP_TENANTS_SECRET` | `tenants-json` (nome do secret no GCP) |
| `SENTRY_DSN_SECRET` | (opcional) nome do secret Sentry |

### 5.3 Disparar deploy

**Actions → Deploy Cloud Run → Run workflow**

| Campo | Valor sugerido |
|-------|----------------|
| gcp_project | `SEU_PROJETO_ID` |
| gcp_region | `southamerica-east1` |
| deploy_web | `true` |
| cors_origins | URL do web após 1º deploy, ou deixe vazio e ajuste depois |

## 6. Redis (opcional, multi-réplica)

1. Crie **Memorystore for Redis** (mesma região)
2. Configure **Serverless VPC Access connector**
3. No Cloud Run API: `--vpc-connector=CONNECTOR --set-env-vars REDIS_URL=redis://IP:6379/0`

## 7. Checklist pós-deploy

- [ ] `GET /v1/health` → `status: ok`, `gemini_available: true`
- [ ] Frontend abre e chama API (sem erro CORS)
- [ ] `AUTH_REQUIRED=true` + tenant de produção
- [ ] Auditoria e export CSV funcionando
- [ ] Sentry/Slack (se configurados)

## Referências

- `ops/DEPLOY.md` — visão geral
- `scripts/deploy_gcp.ps1` — script PowerShell
- `.github/workflows/deploy-cloud-run.yml` — pipeline GitHub
