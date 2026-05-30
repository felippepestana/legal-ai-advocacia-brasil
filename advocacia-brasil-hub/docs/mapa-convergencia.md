# Mapa de convergência — arquivos atuais → solução única

## Situação atual (raiz da pasta)

~50 arquivos **planos**, sem `src/`, sem API, frontend desconectado, **3 versões** por domínio.

## Estrutura alvo

```
legal-ai-platform/
├── advocacia-brasil-hub/          # Este hub (conhecimento + agent)
├── apps/web/                      # React/Next (substitui App.jsx solto)
├── services/
│   ├── api/                       # FastAPI BFF
│   ├── documents/                 # análise + geração + validação
│   ├── search/
│   ├── calculator/
│   ├── deadlines/
│   ├── workflows/
│   └── assistant/
├── packages/legal_core/           # ontologia + validadores BR
├── legacy/manus-export/           # cópia dos .py duplicados (referência)
└── tests/
```

## Tabela de consolidação

| Domínio | Manter (canônico) | Fundir / extrair | Arquivar (legacy) |
|---------|-------------------|------------------|-------------------|
| Documentos – análise | `enhanced_document_analyzer.py` | — | `advanced_document_analyzer.py` |
| Documentos – geração | `enhanced_document_generator.py` | Validador CPC de `advanced_document_features.py` → `packages/legal_core/validators/` | `document_generator.py`, resto de `advanced_document_features.py` após extração |
| Pesquisa | `enhanced_intelligent_search.py` | Semântica de `advanced_search_features.py` quando houver API | `intelligent_search.py` |
| Calculadora | `enhanced_legal_calculator.py` | Tipos extras de `advanced_calculator_features.py` se faltarem | `legal_calculator.py` |
| Prazos | `deadline_manager.py` | Reimplementar stub `enhanced_deadline_manager.py` | — |
| Workflows | `enhanced_workflow_engine.py` | — | `advanced_workflow_engine.py` |
| Assistente | `enhanced_virtual_assistant.py` | — | `ai_assistant.py` |
| Analytics | `enhanced_analytics_engine.py` | KPIs de `advanced_analytics_features.py` | `analytics_engine.py` |

## Documentos `.md` da raiz

| Arquivo | Destino no hub |
|---------|----------------|
| `LegalAI Platform - *.md` | Fundir em `docs/produto-unico-visao.md` |
| `Documentação Técnica Final` | Substituir por `docs/arquitetura.md` (a criar na Fase 1) |
| `Relatório Final de Validação` | `docs/historico-validacao-manus.md` (referência) |
| Planos de teste / melhorias | `docs/roadmap-qa.md` (backlog) |
| `todo.md` | Issues no Git / `docs/roadmap-qa.md` |

## Skills externas (repositório do usuário)

| Skill | Relação com o produto |
|-------|------------------------|
| `local-legal-seo-audit` | **Fora** do core — marketing do escritório |
| `legal-advisor` | **Parcial** — só LGPD, termos, DPA do software |
| Skills deste hub (`.cursor/skills/`) | **Dentro** — análise, peças, prazos, pesquisa BR |

## Passos executáveis (sprint 1)

1. Criar repositório Git; copiar `advocacia-brasil-hub/` e módulos canônicos para `services/`.
2. Gerar `packages/legal_core` a partir dos YAML em `ontology/`.
3. Implementar `POST /documents/analyze` e `POST /deadlines/calculate` com schemas do hub.
4. Uma página web: upload → análise → exibir entidades CNJ/CPF/valor.
5. Marcar arquivos legacy e parar de editar duplicatas.
