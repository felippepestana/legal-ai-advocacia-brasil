# Cria um Log Sink para reter a trilha de auditoria LGPD (logger ai_audit) a longo prazo.
#
# A API emite cada evento de auditoria de IA para o Cloud Logging (logger "ai_audit",
# campo jsonPayload.audit) quando LOG_FORMAT=json. O Cloud Logging tem retencao padrao
# de 30 dias; para compliance LGPD convem exportar esses eventos para um destino
# duravel (GCS por padrao, ou BigQuery para consulta SQL).
#
# Uso:
#   .\scripts\setup_audit_log_sink.ps1 -ProjectId sistemalabadvia
#   .\scripts\setup_audit_log_sink.ps1 -ProjectId sistemalabadvia -Destination bigquery
#
# Pre-requisitos: gcloud autenticado com permissao para criar sinks/buckets/datasets
# (roles/logging.configWriter + roles/storage.admin ou roles/bigquery.admin).
param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectId,
    [ValidateSet("gcs", "bigquery")]
    [string]$Destination = "gcs",
    [string]$Region = "southamerica-east1",
    [string]$SinkName = "advocacia-ai-audit-sink",
    [string]$BucketName = "",
    [string]$DatasetName = "ai_audit",
    # Retencao em dias (LGPD: ajuste conforme sua politica; padrao ~5 anos)
    [int]$RetentionDays = 1825
)

$ErrorActionPreference = "Stop"

# Filtro: o logger "ai_audit" é específico da aplicação, então não restringimos
# por resource.type — isso mantém o sink resiliente a migrações de infra
# (Cloud Run Jobs, GKE, Compute Engine, etc.).
$Filter = 'jsonPayload.logger="ai_audit"'

Write-Host "==> Projeto: $ProjectId | Destino: $Destination | Filtro: $Filter"

if ($Destination -eq "gcs") {
    if (-not $BucketName) { $BucketName = "$ProjectId-ai-audit-logs" }
    $sinkDest = "storage.googleapis.com/$BucketName"

    Write-Host "==> Criando bucket gs://$BucketName (se nao existir)..."
    $exists = gcloud storage buckets list --project $ProjectId --filter "name=$BucketName" --format "value(name)"
    if (-not $exists) {
        gcloud storage buckets create "gs://$BucketName" `
            --project $ProjectId `
            --location $Region `
            --uniform-bucket-level-access
    }

    Write-Host "==> Aplicando retencao de $RetentionDays dias (bucket lock opcional)..."
    gcloud storage buckets update "gs://$BucketName" --retention-period "${RetentionDays}d"

    $writerRole = "roles/storage.objectCreator"
    $grantCmd = {
        param($member)
        gcloud storage buckets add-iam-policy-binding "gs://$BucketName" `
            --member $member --role $writerRole
    }
}
else {
    $sinkDest = "bigquery.googleapis.com/projects/$ProjectId/datasets/$DatasetName"

    Write-Host "==> Criando dataset BigQuery $DatasetName (se nao existir)..."
    $exists = bq ls --project_id=$ProjectId --datasets --format=json | Select-String -SimpleMatch "`"$DatasetName`""
    if (-not $exists) {
        bq --project_id=$ProjectId --location=$Region mk --dataset `
            --description "Trilha de auditoria LGPD (ai_audit)" $DatasetName
    }

    # Menor privilégio: concede a permissão apenas no dataset (não no projeto inteiro).
    $writerRole = "roles/bigquery.dataEditor"
    $grantCmd = {
        param($member)
        bq add-iam-policy-binding --member "$member" --role $writerRole "${ProjectId}:${DatasetName}"
    }
}

Write-Host "==> Criando/atualizando sink '$SinkName' -> $sinkDest ..."
# Checagem por listagem (exit 0 mesmo quando não existe) — robusta a
# $PSNativeCommandUseErrorActionPreference.
$sinkExists = gcloud logging sinks list --project $ProjectId --filter "name=$SinkName" --format "value(name)"
if ($sinkExists) {
    gcloud logging sinks update $SinkName $sinkDest --project $ProjectId --log-filter "$Filter"
}
else {
    $extra = @()
    if ($Destination -eq "bigquery") { $extra += "--use-partitioned-tables" }
    gcloud logging sinks create $SinkName $sinkDest --project $ProjectId --log-filter "$Filter" @extra
}

# A identidade de escritor do sink precisa de permissao no destino
$writer = gcloud logging sinks describe $SinkName --project $ProjectId --format "value(writerIdentity)"
Write-Host "==> Concedendo $writerRole a $writer ..."
& $grantCmd $writer

Write-Host ""
Write-Host "==> Log Sink configurado."
Write-Host "    Sink:    $SinkName"
Write-Host "    Destino: $sinkDest"
Write-Host "    Filtro:  $Filter"
Write-Host ""
Write-Host "Eventos novos de ai_audit passam a ser exportados automaticamente."
Write-Host "Verifique em: Cloud Logging > Log Router > $SinkName"
