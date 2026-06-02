# Verifica configuracao local e (opcional) producao
param(
    [switch]$Production,
    [string]$ApiUrl = "https://advocacia-api-634789300838.southamerica-east1.run.app"
)

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
$ok = $true

function Write-Check($label, $pass, $detail) {
    $script:ok = $ok -and $pass
    $icon = if ($pass) { "[OK]" } else { "[!!]" }
    Write-Host "$icon $label" -ForegroundColor $(if ($pass) { "Green" } else { "Yellow" })
    if ($detail) { Write-Host "    $detail" }
}

Write-Host "`n=== Legal AI — verificacao de configuracao ===`n" -ForegroundColor Cyan

Write-Check ".env existe" (Test-Path ".env") "Execute: .\scripts\setup_dev.ps1"
if (Test-Path ".env") {
    $envContent = Get-Content ".env" -Raw
    $geminiKey = [regex]::Match($envContent, '(?m)^GEMINI_API_KEY=(\S+)').Groups[1].Value
    $gcpProject = [regex]::Match($envContent, '(?m)^GOOGLE_CLOUD_PROJECT=(\S+)').Groups[1].Value
    $backend = [regex]::Match($envContent, '(?m)^AI_BACKEND=(\S+)').Groups[1].Value
    if (-not $backend) { $backend = if ($gcpProject -and -not $geminiKey) { 'vertex' } else { 'api_key' } }
    $iaOk = ($backend -eq 'api_key' -and $geminiKey) -or ($backend -eq 'vertex' -and $gcpProject)
    Write-Check "IA configurada (GEMINI_API_KEY ou Vertex)" $iaOk `
        "Edite .env: GEMINI_API_KEY (https://aistudio.google.com/apikey) ou AI_BACKEND=vertex + GOOGLE_CLOUD_PROJECT"
}

Write-Check "config/tenants.json existe" (Test-Path "config\tenants.json") `
    "Copy-Item config\tenants.example.json config\tenants.json"

Write-Check "Pastas data/" (Test-Path "data\audit") "setup_dev.ps1 cria automaticamente"

if (-not $Production) {
    try {
        $r = Invoke-RestMethod -Uri "http://127.0.0.1:8000/v1/health" -TimeoutSec 3
        Write-Check "API local responde" $true "version=$($r.version) gemini=$($r.gemini_available)"
    } catch {
        Write-Check "API local responde" $false "Inicie: python -m uvicorn services.api.main:app --port 8000"
    }
}

if ($Production) {
    try {
        $r = Invoke-RestMethod -Uri "$ApiUrl/v1/health" -TimeoutSec 15
        Write-Check "API producao /v1/health" ($r.status -eq "ok") `
            "v=$($r.version) auth=$($r.auth_required) tenants=$($r.tenants_configured) gemini=$($r.gemini_available)"
    } catch {
        Write-Check "API producao" $false $_.Exception.Message
    }
}

Write-Host "`nSecrets GitHub (repo):" -ForegroundColor Cyan
gh secret list --repo felippepestana/legal-ai-advocacia-brasil 2>$null

Write-Host "`nGCP projeto ativo:" -ForegroundColor Cyan
gcloud config get-value project 2>$null

if (-not $ok) {
    Write-Host "`nAjuste os itens [!!] e consulte ops/CONFIGURACAO.md`n" -ForegroundColor Yellow
    exit 1
}
Write-Host "`nConfiguracao basica OK. Detalhes: ops/CONFIGURACAO.md`n" -ForegroundColor Green
