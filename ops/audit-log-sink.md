# Retenção de longo prazo da trilha de auditoria LGPD

A API emite cada evento de auditoria de IA para o **Cloud Logging** (logger `ai_audit`,
campo `jsonPayload.audit`) quando `LOG_FORMAT=json`. O evento contém apenas `prompt_hash`
+ metadados (tenant, operação, modelo, latência, contagens) — **sem texto integral do
prompt**, alinhado à LGPD.

O Cloud Logging tem **retenção padrão de 30 dias**. Para compliance, exporte os eventos
para um destino durável via **Log Sink**.

## Setup rápido (script)

GCS (padrão, retenção ~5 anos):

```powershell
.\scripts\setup_audit_log_sink.ps1 -ProjectId sistemalabadvia
```

BigQuery (consulta SQL, tabelas particionadas por dia):

```powershell
.\scripts\setup_audit_log_sink.ps1 -ProjectId sistemalabadvia -Destination bigquery
```

O script cria o destino (bucket/dataset), cria o sink filtrando
`jsonPayload.logger="ai_audit"` e concede à identidade de escritor do sink a permissão
necessária no destino.

## Passos manuais equivalentes (GCS)

```bash
PROJECT=sistemalabadvia
REGION=southamerica-east1
BUCKET=${PROJECT}-ai-audit-logs
FILTER='resource.type="cloud_run_revision" AND jsonPayload.logger="ai_audit"'

# 1. Bucket durável com retenção (~5 anos)
gcloud storage buckets create gs://$BUCKET --project=$PROJECT \
  --location=$REGION --uniform-bucket-level-access
gcloud storage buckets update gs://$BUCKET --retention-period=1825d

# 2. Sink
gcloud logging sinks create advocacia-ai-audit-sink \
  storage.googleapis.com/$BUCKET --project=$PROJECT --log-filter="$FILTER"

# 3. Permissão para a identidade de escritor do sink
WRITER=$(gcloud logging sinks describe advocacia-ai-audit-sink \
  --project=$PROJECT --format='value(writerIdentity)')
gcloud storage buckets add-iam-policy-binding gs://$BUCKET \
  --member="$WRITER" --role=roles/storage.objectCreator
```

## Observações

- O sink exporta **apenas eventos novos** (a partir da criação). O histórico anterior
  permanece sujeito à retenção do Cloud Logging.
- Para imutabilidade (anti-tamper), aplique **Bucket Lock** após validar a retenção:
  `gcloud storage buckets update gs://$BUCKET --lock-retention-period` (irreversível).
- Consultas operacionais da trilha: `ops/cloud-logging-queries.md`.
