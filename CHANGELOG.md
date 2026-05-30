# Changelog

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
