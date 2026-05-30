# Deploy manual API + Web no Google Cloud Run
# Uso: .\scripts\deploy_gcp.ps1 -ProjectId meu-projeto -Region southamerica-east1
param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectId,
    [string]$Region = "southamerica-east1",
    [string]$ApiService = "advocacia-api",
    [string]$WebService = "advocacia-web",
    [switch]$ApiOnly,
    [switch]$WebOnly
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

Write-Host "==> Projeto: $ProjectId | Região: $Region"

if (-not $WebOnly) {
    Write-Host "==> Build e deploy API..."
    gcloud builds submit --project $ProjectId --tag "gcr.io/$ProjectId/${ApiService}:latest" .

    $envVars = @(
        "AI_BACKEND=vertex",
        "GOOGLE_CLOUD_PROJECT=$ProjectId",
        "VERTEX_LOCATION=$Region",
        "LOG_FORMAT=json",
        "RATE_LIMIT_ENABLED=true",
        "SEARCH_CACHE_ENABLED=true",
        "AI_AUDIT_ENABLED=true",
        "AUTH_REQUIRED=true"
    ) -join ","

    gcloud run deploy $ApiService `
        --project $ProjectId `
        --image "gcr.io/$ProjectId/${ApiService}:latest" `
        --region $Region `
        --platform managed `
        --allow-unauthenticated `
        --memory 1Gi `
        --cpu 1 `
        --min-instances 0 `
        --max-instances 10 `
        --set-env-vars $envVars

    Write-Host ""
    Write-Host "Configure no Cloud Run (Variables & Secrets):"
    Write-Host "  - TENANTS_JSON ou Secret Manager -> tenants-json"
    Write-Host "  - CORS_ORIGINS (URL do frontend)"
    Write-Host "  - SENTRY_DSN, SLACK_WEBHOOK_URL, REDIS_URL (opcional)"
}

if (-not $ApiOnly) {
    $apiUrl = gcloud run services describe $ApiService `
        --project $ProjectId `
        --region $Region `
        --format "value(status.url)"

    if (-not $apiUrl) {
        Write-Error "URL da API não encontrada. Faça deploy da API primeiro ou omita -WebOnly."
    }

    Write-Host "==> Build Web com VITE_API_URL=$apiUrl"
    gcloud builds submit --project $ProjectId `
        --config cloudbuild.web.yaml `
        --substitutions "_VITE_API_URL=$apiUrl,_IMAGE=gcr.io/$ProjectId/${WebService}:latest"

    gcloud run deploy $WebService `
        --project $ProjectId `
        --image "gcr.io/$ProjectId/${WebService}:latest" `
        --region $Region `
        --platform managed `
        --allow-unauthenticated `
        --memory 512Mi `
        --port 8080

    $webUrl = gcloud run services describe $WebService `
        --project $ProjectId `
        --region $Region `
        --format "value(status.url)"

    Write-Host ""
    Write-Host "==> Deploy concluído"
    Write-Host "API:  $apiUrl"
    Write-Host "Web:  $webUrl"
    Write-Host "Health: $apiUrl/v1/health"
    Write-Host ""
    Write-Host "Atualize CORS_ORIGINS da API com: $webUrl"
}
