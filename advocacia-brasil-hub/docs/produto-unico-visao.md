# Produto único — Plataforma de Advocacia Brasil

## Proposta de valor

Sistema integrado para escritórios e advogados autônomos que cobre o **ciclo operacional da advocacia** no Brasil:

```mermaid
flowchart LR
  A[Captação / Cliente] --> B[Análise documental]
  B --> C[Pesquisa normativa]
  C --> D[Estratégia e peças]
  D --> E[Prazos e agenda]
  E --> F[Audiências / cumprimento]
  F --> G[Analytics e KPIs]
```

## Oito capacidades (uma implementação cada)

| # | Capacidade | Uso na advocacia BR | Módulo canônico |
|---|------------|---------------------|-----------------|
| 1 | Análise documental | Classificar peça, extrair partes, valores, CNJ, riscos | `enhanced_document_analyzer.py` |
| 2 | Workflows | Automação pós-análise (tarefas, e-mail, alertas) | `enhanced_workflow_engine.py` |
| 3 | Assistente | Consulta orientativa com base normativa (não substitui advogado) | `enhanced_virtual_assistant.py` |
| 4 | Prazos | Contagem em dias úteis, feriados BR, alertas | `deadline_manager.py` |
| 5 | Analytics | Desempenho por área, vara, tipo de ação | `enhanced_analytics_engine.py` |
| 6 | Geração de peças | Templates + IA com validação CPC | `enhanced_document_generator.py` + validador em `advanced_document_features.py` |
| 7 | Pesquisa | Jurisprudência, lei, doutrina (futuro: APIs reais) | `enhanced_intelligent_search.py` |
| 8 | Calculadora | Trabalhista, cível, atualização, honorários | `enhanced_legal_calculator.py` |

## Princípios do ordenamento brasileiro

- **Competência e rito**: CPC (processo cível), CLT + CPC subsidiário (trabalhista), CPP (penal), leis esparsas por área.
- **Numeração única**: padrão CNJ para processos (`ontology/entidades-juridicas.yaml`).
- **Prazos**: dias úteis salvo lei em contrário; feriados nacionais e móveis (`deadline_manager.py`).
- **Peças iniciais**: requisitos do art. 319 CPC refletidos em skills e validador.
- **Ética**: atuação compatível com Código de Ética OAB — IA como apoio, revisão humana obrigatória em peças e estratégia.

## O que NÃO é escopo do produto core

- SEO de site de escritório (skill externa `local-legal-seo-audit`).
- Políticas SaaS genéricas GDPR-first (skill `legal-advisor` — usar só para LGPD/privacidade do produto).

## Definição de "pronto" (MVP full)

- [ ] Uma tela por capacidade consumindo API real
- [ ] Ontologia YAML = enums Python
- [ ] Geração de petição inicial com checklist art. 319
- [ ] Prazo de contestação calculado com feriados BR
- [ ] Disclaimer e trilha de auditoria (LGPD)
- [ ] Provedor de IA configurável (Vertex/Gemini)
