---
name: prazos-processuais-brasil
description: Calcula e explica prazos processuais brasileiros em dias úteis com feriados nacionais. Use para contestação, recursos, manifestações e alertas de vencimento.
---

# Prazos processuais — Brasil

## Quando usar

- Calcular vencimento a partir de data de citação/intimação/publicação
- Validar implementação de `deadline_manager.py`
- Configurar alertas de workflow

## Regras

1. Contagem em **dias úteis** (regra geral CPC), salvo lei específica
2. Excluir feriados nacionais fixos e móveis — ver `ontology/prazos-processuais.yaml`
3. Não considerar o dia do começo; incluir o dia do vencimento se útil
4. Recesso forense e calendário local: marcar como `planejado` — exigir confirmação humana

## Prazos padrão (dias úteis) — referência

| Tipo | Dias |
|------|------|
| Contestação | 15 |
| Recurso / Embargos | 15 |
| Réplica | 10 |
| Manifestação | 15 |
| Juntada de documentos | 5 |

Ajustar conforme rito e decisão judicial específica.

## Saída esperada

- `data_vencimento` (ISO 8601)
- `dias_uteis_contados`
- `feriados_excluidos`
- `observacoes` (ex.: necessidade de verificar suspensão em recesso)

## Código canônico

`deadline_manager.py` — `BrazilianHolidayCalculator`, `DeadlineCalculator`
