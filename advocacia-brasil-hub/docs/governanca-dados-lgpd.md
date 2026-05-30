# Governança de dados — advocacia e LGPD

## Papéis

| Papel | Dados típicos | Base legal (orientação) |
|-------|---------------|-------------------------|
| Escritório (controlador) | Clientes, processos, peças | Execução de contrato / legítimo interesse |
| Plataforma (operador) | Processamento sob instrução do escritório | Contrato de tratamento (DPA) |

## Classificação de documentos

- **Públicos**: jurisprudência, leis (sem restrição de upload).
- **Confidenciais**: petições, contratos, provas — criptografia em repouso, acesso por tenant.
- **Sensíveis**: saúde, criança, dados de terceiros em processos — minimizar retenção; não usar para treinar modelo global.

## Regras de produto

1. **Revisão humana** obrigatória antes de protocolo de peça gerada por IA.
2. **Disclaimer** visível: ferramenta de apoio, não substitui advogado.
3. **Logs**: quem analisou qual documento, quando; sem gravar conteúdo integral em log se não necessário.
4. **Retenção**: política configurável por escritório (ex.: 90 dias para rascunhos de IA).
5. **Exportação e exclusão**: atender direitos do titular via painel do escritório.
6. **Subprocessadores**: Vertex/Gemini, storage cloud — listar em DPA.

## Integração com skills

- Agente deve citar `advocacia-brasil-hub/docs/governanca-dados-lgpd.md` ao lidar com uploads ou dados de clientes.
- Nunca enviar dados identificáveis a treinamento de terceiros sem consentimento explícito.
