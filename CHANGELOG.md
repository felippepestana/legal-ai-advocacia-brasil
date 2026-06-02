# Changelog

## [2.0.2] — 2026-06-01

### CI/CD e produção

- **GitHub Actions**: deploy Cloud Run estável — build assíncrono com polling (`gcloud builds describe`) em substituição ao streaming de logs e ao comando `gcloud builds wait` (indisponível no runner).
- **IAM GCP**: `roles/artifactregistry.reader` para `github-deploy`, compute default e Cloud Run robot SA — corrige `PERMISSION_DENIED` no `gcloud run deploy`.
- **WIF**: documentação de `serviceAccountTokenCreator` e mapeamento `attribute.repository` em `ops/GCP-SETUP.md`.
- **Deploy validado**: API + Web em `sistemalabadvia` / `southamerica-east1` com `AUTH_REQUIRED=true`, `tenants_configured: 2`, CORS alinhado ao frontend.

### URLs de produção

- Web: https://advocacia-web-634789300838.southamerica-east1.run.app
- API: https://advocacia-api-634789300838.southamerica-east1.run.app
- Health: `/v1/health`

---

## [2.0.1] — 2026-06-01

### Hotfix produção

- Dependência `openai` adicionada ao `requirements.txt` (container Cloud Run não subia sem ela).
- Auth multi-tenant via Secret Manager (`tenants-json`) e `AUTH_REQUIRED=true` em produção.
- Primeiro deploy manual GCP + secrets GitHub (`GCP_TENANTS_SECRET`, WIF).

---

## [2.0.0] — 2026-05-27

### Escopo V2 — Jurídico e gestão

A **V2** consolida a plataforma exclusivamente para **advocacia no ordenamento brasileiro** e **ferramentas de gestão e administração**:

**Módulos jurídicos**

- Análise documental inteligente
- Validação CPC (petição inicial)
- Gestão de prazos processuais (BR)
- Calculadora jurídica (trabalhista/cível)
- Pesquisa normativa e jurisprudencial
- Geração de peças com revisão humana

**Gestão e administração**

- Workflows automatizados
- Assistente jurídico com IA
- Analytics de performance
- Auditoria LGPD (JSONL + export CSV + alertas)

### Removido / fora de escopo

- Funcionalidades de **odontologia** e demais verticais de saúde/clínica — **não fazem parte da V2** e não estão presentes no código ativo (`apps/web`, `services/api`, `services/modules`).
- Integrações Stripe (permanecem fora do escopo de deploy).

### Infraestrutura

- API FastAPI `/v1` com multi-tenant, rate limit, cache Redis opcional
- Frontend React (10 módulos) + Docker Compose + deploy Cloud Run
- CI/CD GitHub Actions (`ci.yml`, `deploy-cloud-run.yml`)

### Versões

- API e health: `2.0.0`
- Frontend npm: `2.0.0`
