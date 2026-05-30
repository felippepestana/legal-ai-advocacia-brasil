# Sincroniza D:\DEV\LEGA-AI -> Google Drive (preserva node_modules locais em cada lado)
$src = "D:\DEV\LEGA-AI"
$dst = "k:\Meu Drive\SOLUÇÃO JURIDICA IA legal performance MANUS PARA GOOGLE"

if (-not (Test-Path $dst)) {
    Write-Error "Destino não encontrado: $dst"
    exit 1
}

Write-Host "Sincronizando $src -> $dst ..."
robocopy $src $dst /MIR /XD node_modules __pycache__ .pytest_cache .venv venv data apps\web\dist .git /XF desktop.ini
$code = $LASTEXITCODE
if ($code -ge 8) { exit $code }
Write-Host "Concluído."
