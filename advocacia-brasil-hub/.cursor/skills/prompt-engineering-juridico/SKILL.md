---
name: prompt-engineering-juridico
description: Cria ou revisa prompts da plataforma jurídica brasileira usando Fundamentos de Prompt 101 com adaptações CPC/LGPD/OAB. Use ao adicionar capacidades de IA, refatorar system prompts ou alinhar Vertex/Gemini ao hub.
---

# Prompt engineering — Advocacia Brasil

## Referências obrigatórias

1. Infográfico: `advocacia-brasil-hub/assets/regras_de_prompt.png`
2. Mapa adaptado: `docs/fundamentos-prompt-101-juridico.md`
3. Índice JSON: `config/mapa-fundamentos-prompt.json`
4. Template: `prompts/_template-prompt-juridico.md`

## Procedimento para novo prompt de produção

1. Identificar capacidade em `config/matriz-capacidades.json`.
2. Copiar `_template-prompt-juridico.md`.
3. Aplicar fundamentos listados em `mapa-fundamentos-prompt.json` para essa capacidade.
4. Adicionar few-shot em `prompts/exemplos/` se saída estruturada (#7, #18).
5. Ligar schema em `schemas/` se resposta for JSON.
6. Atualizar skill de domínio (ex.: `analise-documental-brasil`).
7. **Não** usar #6 (gorjeta) nem #15 (modo ensino) em runtime.

## Ajustes jurídicos obrigatórios

- Proibir alucinação de normas e processos (#4, #10 reformulado).
- Delimitadores `<<<>>>` para dados do cliente (#16).
- Revisão humana em geração de peças.
- Tamanho: curto/médio/longo conforme tabela em `fundamentos-prompt-101-juridico.md` (#26–28).

## Anti-padrões

- Prompts genéricos sem público (#2).
- "Não faça X" sem instrução positiva equivalente (#4).
- Peça processual em linguagem coloquial (#11).
- Resposta livre quando API exige JSON (#19).
