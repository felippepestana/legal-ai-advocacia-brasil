# Legal AI Web

Frontend React (Vite) para a API `/v1`.

## Desenvolvimento

1. Na raiz do projeto, suba a API:

```powershell
python -m uvicorn services.api.main:app --reload --port 8000
```

2. Nesta pasta:

```powershell
npm install
npm run dev
```

Abra http://localhost:5173 — o proxy do Vite encaminha `/v1` para `http://127.0.0.1:8000`.

## Produção

```powershell
npm run build
```

Sirva `dist/` com qualquer host estático e defina `VITE_API_URL` para a URL pública da API.

## Abas

| Aba | Endpoint |
|-----|----------|
| Análise documental | `POST /v1/documents/analyze` |
| Validação CPC | `POST /v1/documents/validate` |
| Prazos | `POST /v1/deadlines/calculate` |
| Calculadora | `POST /v1/calculator/run` |
| Pesquisa | `POST /v1/search/query` |
| Peças | `GET /v1/generation/templates`, `POST /v1/generation/generate` |

Opcional: marque **Enriquecer com Gemini** se `GEMINI_API_KEY` estiver no servidor.
