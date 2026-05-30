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

## Auditoria IA — export offline

Os eventos de auditoria ficam em `data/audit/` (JSONL) ou via:

- `GET /v1/audit/recent`
- `GET /v1/audit/export` (CSV)

Para correlacionar com logs de aplicação, filtre por `jsonPayload.operation` contendo `ai_`.

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
