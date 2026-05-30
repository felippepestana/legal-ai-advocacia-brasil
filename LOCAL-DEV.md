# Ambiente local — `D:\DEV\LEGA-AI`

Cópia de desenvolvimento fora do Google Drive (evita falhas do `npm install` em `node_modules`).

## Setup (já executado)

```powershell
cd D:\DEV\LEGA-AI
pip install -r requirements.txt
cd apps\web
npm install
npm run build
python -m pytest D:\DEV\LEGA-AI\tests\ -q
```

## Executar

```powershell
cd D:\DEV\LEGA-AI
.\scripts\run_dev.ps1
```

- API: http://127.0.0.1:8000/docs  
- Web: http://localhost:5173  

## Sincronizar com o Google Drive

Quando alterar arquivos no Drive, rode:

```powershell
.\scripts\sync_from_drive.ps1
```

## Git

Repositório Git ativo nesta pasta (`main`). Commits e push devem ser feitos daqui.
