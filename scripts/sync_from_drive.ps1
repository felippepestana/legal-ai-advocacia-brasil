# Sincroniza código do Google Drive para D:\DEV\LEGA-AI (preserva node_modules local)
$src = "k:\Meu Drive\SOLUÇÃO JURIDICA IA legal performance MANUS PARA GOOGLE"
$dst = "D:\DEV\LEGA-AI"

if (-not (Test-Path $src)) {
    Write-Error "Origem não encontrada: $src"
    exit 1
}

Write-Host "Sincronizando $src -> $dst ..."
robocopy $src $dst /MIR /XD node_modules __pycache__ .pytest_cache .venv venv data apps\web\dist /XF desktop.ini
$code = $LASTEXITCODE
if ($code -ge 8) { exit $code }
Write-Host "Concluído. Rode 'npm install' em apps\web se package.json mudou."
