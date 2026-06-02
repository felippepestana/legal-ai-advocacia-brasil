# Consultas Cloud Logging (Legal AI Platform)

Use com `LOG_FORMAT=json` no Cloud Run. Logs estruturados incluem `level`, `message`, `tenant_id` (quando autenticado) e contexto de requisição.

## Erros da API (últimas 24h)

```
resource.type="cloud_run_revision"
jsonPayload.level="ERROR"
timestamp>="-24h"
```

## Requisições por tenant (contagem)

```
resource.type="cloud_run_revision"
jsonPayload.tenant_id!=""
| stats count() by jsonPayload.tenant_id
```

## Latência média de endpoints (aprox.)

```
resource.type="cloud_run_revision"
jsonPayload.message=~"POST /v1/"
| stats avg(jsonPayload.duration_ms) by jsonPayload.path
```

## Falhas de rate limit (429)

```
resource.type="cloud_run_revision"
httpRequest.status=429
timestamp>="-7d"
| stats count() by httpRequest.requestUrl
```

## Auditoria IA — trilha durável (Cloud Logging)

Com `LOG_FORMAT=json`, cada consulta de IA é registrada de forma **durável** pelo logger
`ai_audit` (sobrevive a reinícios/revisões do Cloud Run, ao contrário de `data/audit/`).
O evento vai em `jsonPayload.audit` (sem texto integral do prompt — apenas `prompt_hash`,
contagens e metadados, alinhado à LGPD):

```
resource.type="cloud_run_revision"
jsonPayload.logger="ai_audit"
timestamp>="-7d"
```

Falhas de IA (alertas):

```
resource.type="cloud_run_revision"
jsonPayload.logger="ai_audit"
jsonPayload.audit.success=false
```

Por tenant / operação:

```
resource.type="cloud_run_revision"
jsonPayload.logger="ai_audit"
| stats count() by jsonPayload.audit.tenant_id, jsonPayload.audit.operation
```

> Para retenção/arquivamento de longo prazo, crie um **Log Sink** (BigQuery ou GCS) filtrando
> `jsonPayload.logger="ai_audit"` — sem mudança de código.

### Export in-app (instância/dia corrente)

- `GET /v1/audit/recent`
- `GET /v1/audit/export` (CSV)

## Grafana / Looker

1. Conecte o Cloud Logging como fonte de dados no GCP.
2. Importe métricas customizadas a partir dos logs JSON (contadores de erro, latência).
3. Painéis sugeridos:
   - Taxa de erro 5xx
   - Requisições/min por tenant
   - Cache hit ratio (`sources.cache_hit` nos logs de pesquisa, se instrumentado)
   - Status Redis (`redis_connected` no health check via uptime probe)

## Health check para uptime

```
GET /v1/health
```

Campos úteis para alertas: `redis_connected`, `gemini_available`, `sentry_enabled`, `slack_alerts_enabled`.
