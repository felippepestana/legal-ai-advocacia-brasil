# Setup inicial do ambiente local (D:\DEV\LEGA-AI)
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

Write-Host "==> Criando diretórios de dados..."
$dirs = @(
    "data\audit",
    "data\analytics\charts",
    "data\search_cache"
)
foreach ($d in $dirs) {
    New-Item -ItemType Directory -Path $d -Force | Out-Null
}

if (-not (Test-Path "config\tenants.json")) {
    Copy-Item "config\tenants.example.json" "config\tenants.json"
    Write-Host "==> config\tenants.json criado a partir do exemplo"
}

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "==> .env criado — edite GEMINI_API_KEY e demais variáveis"
}

Write-Host "==> Instalando dependências Python..."
pip install -r requirements.txt

Write-Host "==> Instalando dependências Web..."
Set-Location "$root\apps\web"
if (-not (Test-Path "node_modules")) {
    npm install
}

Set-Location $root
Write-Host ""
Write-Host "Setup concluído. Próximos passos:"
Write-Host "  1. Edite .env (GEMINI_API_KEY, etc.)"
Write-Host "  2. .\scripts\run_dev.ps1"
Write-Host "  Ou stack Docker: docker compose up --build"
