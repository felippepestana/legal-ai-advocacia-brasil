---
name: validacao-peticao-cpc
description: Valida petições e peças à luz do CPC/2015 (art. 319 e requisitos formais). Use ao revisar petição inicial, contestação ou minuta antes de protocolo.
---

# Validação de peça — CPC/2015

## Petição inicial (art. 319)

Verificar presença e clareza de:

1. Juízo a que é dirigida
2. Qualificação completa das partes (incl. CPF/CNPJ, endereço, e-mail quando aplicável)
3. Fatos e fundamentos jurídicos do pedido
4. Pedido com especificações
5. Valor da causa
6. Provas com que pretende demonstrar os fatos
7. Opção por audiência de conciliação/mediação

## Requisitos formais recorrentes

- Assinatura do advogado e número OAB
- Data e local
- Procuração nos autos quando representação por advogado

## Procedimento

1. Mapear cada requisito → trecho do documento ou **AUSENTE**
2. Atribuir severidade: `critical` | `warning` | `info`
3. Sugerir redação **sem** fabricar fatos; usar placeholders `[COMPLETAR]`
4. Calcular score: % de itens críticos atendidos

## Saída

| Requisito | Status | Trecho / observação |
|-----------|--------|---------------------|

Incluir `compliance_score` de 0 a 100 e lista priorizada de correções.

## Prompt de produção

`advocacia-brasil-hub/prompts/sistema-validacao-cpc.md` (fundamentos #4, #9, #17, #24)

## Integração com produto

Extrair regras para `packages/legal_core/validators/peticao_inicial.py` a partir deste checklist — manter paridade skill ↔ código ↔ prompt.
