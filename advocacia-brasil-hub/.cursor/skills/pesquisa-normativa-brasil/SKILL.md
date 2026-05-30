---
name: pesquisa-normativa-brasil
description: Estrutura pesquisa jurídica brasileira em legislação, jurisprudência e doutrina com citações verificáveis. Use ao implementar busca, RAG ou respostas do assistente virtual.
---

# Pesquisa normativa — Brasil

## Escopo

- Legislação federal (Planalto e bases oficiais)
- Jurisprudência (STF, STJ, TJs — quando integrado)
- Súmulas e teses repetitivas
- Doutrina apenas se fonte fornecida pelo usuário

## Procedimento

1. Classificar consulta: `legislacao` | `jurisprudencia` | `mista`
2. Identificar área em `ontology/areas-direito.yaml`
3. Expandir sinônimos jurídicos (ex.: "indenização" ↔ "danos morais")
4. Retornar resultados com: título, trecho, fonte, data, tribunal/lei
5. **Nunca** inventar número de processo, súmula ou artigo — marcar `fonte_nao_verificada` se simulado

## Formato de citação sugerido

- Lei: `Lei nº X/AAAA, art. Y`
- Súmula: `Súmula nº X/STJ`
- Acórdão: `TJXX, Apelação nº ..., Rel. ..., j. DD/MM/AAAA`

## Integração futura

Documentar em ADR quando conectar APIs reais (DataJud, tribunais, bases pagas).

## Código canônico

`enhanced_intelligent_search.py` — substituir mocks por conectores indexados
