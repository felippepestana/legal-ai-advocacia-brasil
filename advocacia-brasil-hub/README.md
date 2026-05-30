# Advocacia Brasil Hub

Ponto único de convergência entre **conhecimento jurídico brasileiro**, **skills de agente**, **regras de produto** e **código** da Legal AI Platform.

## Objetivo

Transformar o protótipo Manus (módulos Python soltos + UI mock) em uma **solução full** para advocacia no **ordenamento jurídico brasileiro**, sem duplicar lógica em três camadas (`base` / `enhanced` / `advanced`).

## Como usar este hub

| Pasta | Função |
|-------|--------|
| `docs/` | Visão de produto, mapa de convergência, LGPD e governança |
| `ontology/` | Vocabulário canônico (áreas, peças, prazos, entidades) — fonte da verdade |
| `config/` | Qual arquivo Python vira qual serviço; matriz de capacidades |
| `.cursor/skills/` | Comportamento do agente ao analisar/gerar peças e prazos |
| `.cursor/rules/` | Regras fixas (OAB, CPC, LGPD, citação normativa) |
| `prompts/` | System prompts alinhados à ontologia (Gemini/Vertex) |
| `prompts/exemplos/` | Few-shots (Fundamento #7 / #18) |
| `assets/` | Referência visual `regras_de_prompt.png` (Prompt 101) |
| `schemas/` | Contratos JSON de entrada/saída das APIs |
| `docs/fundamentos-prompt-101-juridico.md` | Mapa dos 28 fundamentos adaptados ao direito BR |
| `docs/solucao-full-analise-v2.md` | Análise consolidada da solução full (v2) |

## Fluxo de harmonização (ordem recomendada)

1. **Ontologia** — alinhar enums e tipos em todo o código aos YAMLs.
2. **Módulos canônicos** — seguir `config/modulos-canonicos.json` (uma versão por domínio).
3. **Skills + rules** — agente e devs seguem o mesmo checklist (ex.: art. 319 CPC).
4. **API** — expor contratos em `schemas/`; frontend consome só a API.
5. **Legado** — mover duplicatas para `legacy/` na raiz do repositório (não apagar de imediato).

## API (implementada)

A API FastAPI está em `services/api/` na raiz do repositório:

- `GET /v1/health`
- `POST /v1/documents/analyze` | `/validate`
- `POST /v1/deadlines/calculate`
- `POST /v1/calculator/run`
- `GET /v1/prompts/{name}`

Ver `README.md` na raiz do projeto para executar com `uvicorn`.

## Próximo passo técnico

Frontend consumindo a API; integração Vertex AI com os prompts deste hub; migrar `.py` da raiz para `services/modules/`.
