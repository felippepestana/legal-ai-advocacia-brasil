---
name: analise-documental-brasil
description: Analisa documentos jurídicos brasileiros (petições, sentenças, contratos) extraindo tipo de peça, entidades CNJ/CPF/CNPJ/OAB, conceitos e riscos. Use ao classificar peças, revisar uploads, implementar OCR+NLP ou auditar enhanced_document_analyzer.
---

# Análise documental — ordenamento brasileiro

## Quando usar

- Upload ou texto de peça processual, decisão, contrato ou parecer
- Implementação ou revisão do serviço `document_analysis`
- Dúvida sobre classificação de documento ou extração de entidades

## Entrada mínima

- Texto do documento (ou PDF convertido)
- Contexto opcional: área do direito, número CNJ, fase processual

## Procedimento

1. Ler `advocacia-brasil-hub/ontology/tipos-documento.yaml` e classificar o documento.
2. Extrair entidades conforme `ontology/entidades-juridicas.yaml`:
   - Número CNJ (padrão oficial)
   - CPF, CNPJ, OAB, valores em R$, datas
3. Identificar conceitos jurídicos relevantes à área (ex.: danos morais, tutela de urgência).
4. Produzir **resumo objetivo** (fatos, pedidos, decisão) sem inventar fatos ausentes no texto.
5. Listar **lacunas** (ex.: ausência de valor da causa em petição inicial).
6. Se petição inicial: acionar skill `validacao-peticao-cpc` no checklist.

## Saída (estrutura)

```json
{
  "document_type": "peticao_inicial",
  "legal_area": "civil",
  "confidence": 0.0,
  "entities": [],
  "legal_concepts": [],
  "summary": "",
  "gaps": [],
  "opportunities": []
}
```

Usar schema completo em `advocacia-brasil-hub/schemas/analise-documento.output.schema.json`.

## Limites

- Não substituir parecer do advogado; sinalizar incerteza quando confidence < 0.7
- Não inferir estratégia processual sem base no texto
- Dados pessoais: não reproduzir em logs; ver governança LGPD

## Prompts (Fundamentos Prompt 101)

- System: `advocacia-brasil-hub/prompts/sistema-analise-documento.md`
- Few-shot: `prompts/exemplos/analise-peticao-inicial.fewshot.json`
- Mapa: `config/mapa-fundamentos-prompt.json` (#3, #7, #12, #16, #18, #19)

## Código de referência

- Módulo canônico: `enhanced_document_analyzer.py`
- Validador CPC (geração): trecho `cpc_requirements` em `advanced_document_features.py`
