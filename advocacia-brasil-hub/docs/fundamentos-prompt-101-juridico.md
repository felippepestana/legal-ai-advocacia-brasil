# Fundamentos de Prompt 101 — adaptação para Advocacia Brasil

Referência visual: `assets/regras_de_prompt.png` (infográfico original).

Este documento mapeia os **28 fundamentos** para a Plataforma Legal AI: o que entra no produto, o que entra só no agente de desenvolvimento e o que **não** se aplica ao tom jurídico formal.

## Legenda de convergência

| Símbolo | Significado |
|---------|-------------|
| ✅ | Incluir no produto (prompts de runtime) |
| 🔧 | Incluir com ajuste para direito BR / OAB / LGPD |
| 🛠️ | Uso em desenvolvimento (Cursor/skills), não em peça para cliente |
| ⏸️ | Não usar no core (treinamento, gamificação, etc.) |

## Mapa dos 28 fundamentos

| # | Fundamento original | Convergência | Ajuste para solução jurídica BR | Onde aplicar |
|---|---------------------|--------------|--------------------------------|--------------|
| 1 | Seja direto; pule polidez | 🔧 | Manter objetividade, mas **tom formal** em peças e pareceres | Prompts de análise; não em minuta protocolável |
| 2 | Especifique o público | ✅ | "Advogado licenciado", "equipe trabalhista", "cliente leigo" | Todos os system prompts |
| 3 | Divida tarefas complexas em passos | ✅ | Pipeline: classificar → extrair → validar CPC → resumir | Skills + orquestração API |
| 4 | Use "faça", evite "não faça" | 🔧 | Preferir instruções positivas; exceção: **proibição explícita** de inventar jurisprudência | Todos os prompts |
| 5 | Peça explicações simples | 🔧 | "Resumo para cliente" vs "análise técnica para advogado" | Assistente + relatórios |
| 6 | Linha de incentivo (gorjeta) | ⏸️ | Evitar em produção; pode distorcer prioridades legais | — |
| 7 | Few-shot com exemplos | ✅ | Exemplos de JSON de análise, trecho de petição, citação STJ | `prompts/exemplos/` |
| 8 | Estruture com seções e quebras | ✅ | Cabeçalhos: CONTEXTO, DOCUMENTO, TAREFA, SAÍDA | Template `_template-prompt-juridico.md` |
| 9 | "Sua tarefa é" / "Você DEVE" | ✅ | Obrigatoriedade para schema JSON, CPC, LGPD | System prompts |
| 10 | "Você será penalizado" | 🔧 | Reformular: **"Respostas fora do schema serão rejeitadas"** / sem citação falsa | Validação + prompts |
| 11 | Linguagem natural humana | 🔧 | PT-BR **jurídico formal**; evitar coloquialismo em peças | Geração de peças |
| 12 | "Pense passo a passo" | ✅ | Raciocínio em cadeia antes do JSON final (oculto do usuário se necessário) | Análise, pesquisa, fundamentação |
| 13 | Respostas imparciais | ✅ | Crítico para YMYL jurídico; sem estereótipos sobre partes | Todos |
| 14 | Perguntas esclarecedoras | ✅ | Falta valor da causa, área, tipo de peça → perguntar antes de gerar | Assistente, geração |
| 15 | Ensine-me + teste-me | ⏸️ | Modo treino opcional futuro; não é MVP advocacia | — |
| 16 | Delimitadores `{ }` | ✅ | Separar TEXTO_DO_DOCUMENTO, DADOS_ESTRUTURADOS, SAÍDA_JSON | Todos os prompts runtime |
| 17 | Repetir palavra-chave | 🔧 | Repetir "apenas no texto fornecido" / "art. 319 CPC" | Validação petição |
| 18 | Passo a passo + few-shot | ✅ | Combinar #12 e #7 nos fluxos principais | Análise documental |
| 19 | Primer de saída no final | ✅ | Terminar com: `Responda APENAS com JSON válido:` | Análise, APIs |
| 20 | Peça escrita detalhada | ✅ | "Minuta completa com fatos, direito, pedidos e valor da causa" | Geração de peças |
| 21 | Edição preservando estilo | ✅ | Revisão de minuta do escritório sem alterar tese | Skill futura `revisao-minuta` |
| 22 | Código multi-arquivo via script | 🛠️ | Agentes Cursor harmonizando hub + services | Desenvolvimento |
| 23 | Continuação com início fornecido | ✅ | Completar petição/recurso a partir de rascunho | Geração + editor |
| 24 | Requisitos exatos (palavras-chave) | ✅ | Ontologia YAML + checklist CPC | Hub + validadores |
| 25 | Imite linguagem da amostra | ✅ | Estilo do escritório (tom, vocabulário, estrutura) | Geração + fine-tuning futuro |
| 26 | 50–100 palavras (tarefa simples) | 🔧 | Classificar tipo de documento, extrair CNJ | Prompts curtos |
| 27 | 150–300 palavras (moderado) | 🔧 | Resumo + entidades + lacunas | Análise padrão |
| 28 | 300–500 palavras (multi-partes) | 🔧 | Análise + fundamentação + validação + pesquisa | Orquestração multi-prompt |

## Tamanho de prompt por capacidade (produto)

| Capacidade | Fundamentos prioritários | Tamanho alvo (#26–28) |
|------------|-------------------------|------------------------|
| Classificação rápida | 2, 8, 16, 19, 26 | Curto |
| Análise documental | 3, 7, 12, 13, 16, 18, 19, 27 | Médio |
| Validação CPC | 4, 9, 17, 24 | Médio |
| Geração de peça | 2, 14, 20, 23, 25, 28 | Longo (ou cadeia de prompts) |
| Pesquisa normativa | 12, 13, 24 + proibir alucinação | Médio |
| Prazos | 24 apenas (determinístico; LLM opcional para explicar) | Curto / sem LLM |

## Princípios que viram regra de produto (não negociáveis)

1. **Não inventar** norma, súmula, processo ou fato (#4, #10, #13).
2. **Schema obrigatório** em análise (#9, #16, #19).
3. **Revisão humana** antes de protocolo (#2 público = advogado).
4. **Delimitadores** entre dado do cliente e instrução (#16).
5. **Passo a passo** interno para raciocínio jurídico (#12, #18).

## Arquivos derivados no hub

- `prompts/_template-prompt-juridico.md` — template único
- `prompts/exemplos/` — few-shots
- `config/mapa-fundamentos-prompt.json` — índice máquina
- `.cursor/skills/prompt-engineering-juridico/` — para evoluir prompts com segurança
