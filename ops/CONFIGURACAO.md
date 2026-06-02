# Configuração completa — APIs, secrets e ambientes

Guia único para **desenvolvimento local**, **produção (GCP)** e **CI/CD (GitHub)**.

---

## Visão geral das integrações

| Integração | Obrigatória? | Onde configurar | Uso na plataforma |
|------------|--------------|-----------------|-------------------|
| **Vertex AI (Gemini)** | Sim (prod) | GCP + Cloud Run env | IA em todos os módulos (análise, peças, assistente, etc.) |
| **Gemini API Key** | Sim (dev local) | `.env` → `GEMINI_API_KEY` | Mesmo, via Google AI Studio |
| **Tenants (X-API-Key)** | Sim (prod) | `config/tenants.json` + Secret Manager | Auth multi-escritório |
| **DataJud (CNJ)** | Não* | `.env` → `DATAJUD_API_KEY` | Pesquisa jurisprudência/processos |
| **jurisprudencias.ai** | Não | `.env` → `JURISPRUDENCIAS_API_TOKEN` | Texto de acórdãos STJ/STF/TJs |
| **Redis** | Não | `REDIS_URL` | Rate limit + cache em multi-réplica |
| **Sentry** | Não | `SENTRY_DSN` + secret GitHub | Erros em produção |
| **Slack** | Não | `SLACK_WEBHOOK_URL` | Alertas de falha IA |

\* DataJud funciona com chave pública padrão do CNJ; você pode definir `DATAJUD_API_KEY` se o CNJ rotacionar.

---

## 1. Google Cloud (produção — já em uso)

**Projeto:** `sistemalabadvia`  
**Região:** `southamerica-east1`

### 1.1 APIs que devem estar habilitadas

No [Console → APIs e serviços](https://console.cloud.google.com/apis/dashboard?project=sistemalabadvia):

- Cloud Run API
- Cloud Build API
- Artifact Registry API
- Vertex AI API
- Secret Manager API
- IAM Service Account Credentials API (Workload Identity)

Ou via CLI:

```powershell
gcloud services enable run.googleapis.com cloudbuild.googleapis.com `
  artifactregistry.googleapis.com aiplatform.googleapis.com `
  secretmanager.googleapis.com iamcredentials.googleapis.com `
  --project=sistemalabadvia
```

### 1.2 Vertex AI (IA em produção)

1. Abra [Vertex AI](https://console.cloud.google.com/vertex-ai?project=sistemalabadvia) e aceite os termos, se pedido.
2. A conta de serviço do Cloud Run precisa de **`roles/aiplatform.user`**:

```powershell
$PROJECT = "sistemalabadvia"
$PN = gcloud projects describe $PROJECT --format="value(projectNumber)"
$SA = "$PN-compute@developer.gserviceaccount.com"
gcloud projects add-iam-policy-binding $PROJECT `
  --member="serviceAccount:$SA" --role="roles/aiplatform.user"
```

**Variáveis no Cloud Run (API)** — já aplicadas pelo workflow:

| Variável | Valor produção |
|----------|----------------|
| `AI_BACKEND` | `vertex` |
| `GOOGLE_CLOUD_PROJECT` | `sistemalabadvia` |
| `VERTEX_LOCATION` | `southamerica-east1` |
| `GEMINI_MODEL` | (opcional) `gemini-2.0-flash` |

Validação: `GET /v1/health` → `gemini_available: true`, `ai_backend: "vertex"`.

### 1.3 Billing

O projeto precisa ter **faturamento ativo**. Sem billing, Vertex e Cloud Run falham.

---

## 2. Gemini API Key (desenvolvimento local)

Para rodar a API no PC **sem** Vertex:

1. Acesse [Google AI Studio → API Keys](https://aistudio.google.com/apikey).
2. Crie uma chave no projeto Google Cloud (pode ser o mesmo `sistemalabadvia` ou um projeto pessoal).
3. Cole no arquivo `.env` na raiz do repositório:

```env
AI_BACKEND=api_key
GEMINI_API_KEY=sua-chave-aqui
GEMINI_MODEL=gemini-2.0-flash
```

**Limites:** quotas do AI Studio; não use a mesma chave em repositório público.

**Alternativa dev com Vertex:** instale `gcloud`, faça `gcloud auth application-default login` e use:

```env
AI_BACKEND=vertex
GOOGLE_CLOUD_PROJECT=sistemalabadvia
VERTEX_LOCATION=southamerica-east1
```

---

## 3. Multi-tenant (API keys dos escritórios)

### 3.1 Arquivo local

Copie o exemplo e edite:

```powershell
Copy-Item config\tenants.example.json config\tenants.json
```

Formato (`config/tenants.json` — **não commitar**):

```json
[
  {
    "tenant_id": "escritorio-principal",
    "name": "Escritório Principal",
    "api_key": "gere-uma-string-longa-aleatoria",
    "rate_limit_rpm": 120
  }
]
```

Gere chaves seguras (PowerShell):

```powershell
[Convert]::ToBase64String((1..32 | ForEach-Object { Get-Random -Maximum 256 }) -as [byte[]])
```

### 3.2 Variáveis de ambiente

| Ambiente | Configuração |
|----------|--------------|
| Local | `AUTH_REQUIRED=true` + `TENANT_KEYS_PATH=config/tenants.json` |
| Cloud Run | `AUTH_REQUIRED=true` + secret `TENANTS_JSON` ← `tenants-json:latest` |
| Dev sem auth | `AUTH_REQUIRED=false` (apenas testes rápidos) |

### 3.3 Atualizar produção (Secret Manager)

Após editar `config/tenants.json`:

```powershell
gcloud secrets versions add tenants-json `
  --project=sistemalabadvia `
  --data-file=config/tenants.json
```

O Cloud Run usa `tenants-json:latest` automaticamente no próximo deploy (ou force nova revisão no console).

### 3.4 Frontend

1. Abra https://advocacia-web-634789300838.southamerica-east1.run.app  
2. Aba **Auditoria** → campo **API Key** → salvar (vai para `localStorage`, header `X-API-Key`).

---

## 4. Pesquisa jurídica (APIs externas)

### 4.1 DataJud (CNJ)

- Documentação: [DataJud API pública](https://datajud-wiki.cnj.jus.br/api-publica/)
- Endpoint base: `https://api-publica.datajud.cnj.jus.br`
- A plataforma já envia uma **chave pública padrão** embutida no código.
- Para sobrescrever (se o CNJ publicar nova chave):

```env
DATAJUD_API_KEY=sua-chave-cnj
```

### 4.2 jurisprudencias.ai (opcional)

Para texto integral de acórdãos (STJ, STF, TJs):

1. Cadastro em [jurisprudencias.ai](https://jurisprudencias.ai) (plano gratuito disponível).
2. Obtenha o token e configure:

```env
JURISPRUDENCIAS_API_TOKEN=seu-token
```

Sem token, a pesquisa ainda usa DataJud e fontes internas; mensagens no módulo Pesquisa indicam o que falta.

---

## 5. Frontend (Vite / produção)

| Variável | Quando usar |
|----------|-------------|
| *(vazio)* | Dev: Vite faz proxy de `/v1` → `http://127.0.0.1:8000` |
| `VITE_API_URL` | Build apontando para API em outro host |

**Produção (Cloud Run):** o build do workflow injeta `_VITE_API_URL` com a URL da API. O nginx no container do web também pode fazer proxy `/v1` → API.

Arquivo opcional local: `apps/web/.env.local`

```env
# Deixe vazio em dev (proxy Vite). Em build manual para prod:
# VITE_API_URL=https://advocacia-api-634789300838.southamerica-east1.run.app
```

---

## 6. GitHub Actions (CI/CD)

**Settings → Secrets and variables → Actions**

| Secret | Status | Valor / observação |
|--------|--------|-------------------|
| `GCP_WORKLOAD_IDENTITY_PROVIDER` | Configurado | `projects/634789300838/locations/global/workloadIdentityPools/github-pool/providers/github-provider` |
| `GCP_SERVICE_ACCOUNT` | Configurado | `github-deploy@sistemalabadvia.iam.gserviceaccount.com` |
| `GCP_TENANTS_SECRET` | Configurado | `tenants-json` |
| `SENTRY_DSN_SECRET` | Opcional | Nome do secret no GCP com o DSN (ex.: `sentry-dsn`) |

**Disparar deploy:** Actions → **Deploy Cloud Run** → Run workflow

| Input | Valor |
|-------|--------|
| `gcp_project` | `sistemalabadvia` |
| `gcp_region` | `southamerica-east1` |
| `cors_origins` | `https://advocacia-web-634789300838.southamerica-east1.run.app` |
| `deploy_web` | `true` |

---

## 7. Monitoramento opcional

### Sentry

1. Crie projeto em [sentry.io](https://sentry.io).
2. Copie o DSN.
3. No GCP:

```powershell
echo "https://xxx@xxx.ingest.sentry.io/xxx" | gcloud secrets create sentry-dsn --data-file=- --project=sistemalabadvia
```

4. No GitHub: secret `SENTRY_DSN_SECRET` = `sentry-dsn`
5. Variáveis extras no deploy (podem ir no workflow): `SENTRY_ENVIRONMENT=production`, `SENTRY_TRACES_SAMPLE_RATE=0.1`

### Slack

```env
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/T.../B.../xxx
SLACK_ALERTS_ENABLED=true
```

Crie o webhook em [Slack API](https://api.slack.com/messaging/webhooks).

### Redis (multi-instância)

1. [Memorystore for Redis](https://console.cloud.google.com/memorystore/redis?project=sistemalabadvia) na mesma região.
2. [Serverless VPC Access](https://console.cloud.google.com/networking/connectors?project=sistemalabadvia).
3. Cloud Run API: `--vpc-connector=...` e `REDIS_URL=redis://IP:6379/0`

---

## 8. Setup rápido local (checklist)

```powershell
cd D:\DEV\LEGA-AI
.\scripts\setup_dev.ps1          # cria .env, tenants.json, pastas data/
# Edite .env → GEMINI_API_KEY=...
.\scripts\check_config.ps1       # valida o que falta
.\scripts\run_dev.ps1              # API :8000 + Web :5173
```

| Passo | URL / ação |
|-------|------------|
| Health | http://127.0.0.1:8000/v1/health |
| Swagger | http://127.0.0.1:8000/docs |
| App | http://localhost:5173 |
| API Key no UI | Aba Auditoria (se `AUTH_REQUIRED=true`) |

---

## 9. Checklist produção (estado atual)

| Item | Esperado |
|------|----------|
| `/v1/health` | `version: 2.0.2`, `status: ok` |
| IA | `gemini_available: true`, `ai_backend: vertex` |
| Auth | `auth_required: true`, `tenants_configured: 2` |
| CORS | Origin do web permitido |
| Web | https://advocacia-web-634789300838.southamerica-east1.run.app |
| API | https://advocacia-api-634789300838.southamerica-east1.run.app |

---

## 10. Solução de problemas

| Sintoma | Causa provável | Ação |
|---------|----------------|------|
| `gemini_available: false` | Sem `GEMINI_API_KEY` (dev) ou Vertex sem permissão | Ver seções 1.2 e 2 |
| `401` em todos os endpoints | Falta `X-API-Key` ou tenant inválido | Auditoria → API Key; conferir `tenants.json` |
| CORS no browser | `CORS_ORIGINS` sem URL do front | Atualizar Cloud Run ou input do workflow |
| Pesquisa sem acórdãos textuais | Sem `JURISPRUDENCIAS_API_TOKEN` | Seção 4.2 (opcional) |
| CI deploy falha Artifact Registry | IAM | Ver `ops/GCP-SETUP.md` — `artifactregistry.reader` |

---

## Referências

- `ops/GCP-SETUP.md` — primeira implantação GCP + WIF
- `ops/DEPLOY.md` — Docker e deploy manual
- `.env.example` — lista completa de variáveis
- `config/tenants.example.json` — modelo de tenants
