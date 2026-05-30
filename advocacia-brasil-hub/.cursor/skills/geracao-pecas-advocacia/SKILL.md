---
name: geracao-pecas-advocacia
description: Gera minutas de peças e contratos para advocacia brasileira com templates, fundamentação e validação CPC. Use ao criar petições, recursos ou contratos a partir de dados estruturados.
---

# Geração de peças — advocacia BR

## Pré-requisitos

- `template_id` ou tipo em `ontology/tipos-documento.yaml`
- Dados estruturados das partes, fatos, pedidos, valor da causa
- Área do direito definida

## Fluxo

1. Carregar template de `enhanced_document_generator` / biblioteca interna
2. Preencher campos obrigatórios; marcar `[COMPLETAR]` onde faltar dado
3. Gerar fundamentação jurídica **ancorada** na área e fatos fornecidos
4. Rodar `validacao-peticao-cpc` se for peça processual inicial/recursal
5. Entregar minuta + `quality_score` + lista de revisão humana

## Tom e estilo

- Português jurídico formal brasileiro
- Parágrafos numerados em peças processuais quando padrão do escritório
- Pedidos claros e específicos no dispositivo

## Obrigatório na entrega

```
---
AVISO: Minuta gerada com apoio de IA. Revisão e assinatura por advogado habilitado são obrigatórias antes do protocolo.
---
```

## Limites

- Não protocolar automaticamente
- Não garantir êxito processual
- Criminal: exigir revisão reforçada; não gerar sem fatos completos

## Prompts

- `prompts/sistema-geracao-peca.md` (#14, #20, #23, #25, #28)
- `prompts/sistema-fundamentacao-juridica.md`
- Continuação de rascunho: seção `RASCUNHO_PARA_CONTINUAR` no prompt de geração (#23)

## Código canônico

`enhanced_document_generator.py` + validador extraído de `advanced_document_features.py`
