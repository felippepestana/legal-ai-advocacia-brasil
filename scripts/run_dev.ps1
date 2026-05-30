# Inicia API (8000) e frontend Vite (5173) em janelas separadas
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

Write-Host "Iniciando API em http://127.0.0.1:8000 ..."
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "Set-Location '$root'; python -m uvicorn services.api.main:app --reload --host 127.0.0.1 --port 8000"
)

Start-Sleep -Seconds 2

Write-Host "Iniciando frontend em http://localhost:5173 ..."
Set-Location "$root\apps\web"
if (-not (Test-Path "node_modules")) {
    npm install
}
npm run dev
