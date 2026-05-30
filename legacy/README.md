# Módulos legados (export Manus)

Os arquivos `.py` na **raiz do projeto** são o export original do Manus. A API importa os **módulos canônicos** de `services/modules/` (prioridade no `bootstrap.py`).

## Canônicos em `services/modules/`

| Arquivo | Uso na API |
|---------|------------|
| `enhanced_document_analyzer.py` | `POST /v1/documents/analyze` |
| `deadline_manager.py` | `POST /v1/deadlines/calculate` |
| `enhanced_legal_calculator.py` | `POST /v1/calculator/run` |
| `enhanced_document_generator.py` | (futuro) geração de peças |
| `enhanced_intelligent_search.py` | (futuro) pesquisa normativa |
| `enhanced_workflow_engine.py` | (futuro) workflows |
| `enhanced_virtual_assistant.py` | (futuro) assistente |
| `enhanced_analytics_engine.py` | (futuro) analytics |

## Não editar (arquivar mentalmente)

Duplicatas `base` e `advanced_*` quando existir `enhanced_*` equivalente — ver `advocacia-brasil-hub/config/modulos-canonicos.json` → `legacy_archive`.

## Raiz

Cópias na raiz permanecem como referência do export Manus; prefira editar em `services/modules/`.
