# Escopo V2 — Plataforma Jurídica Advocacia Brasil

**Versão:** 2.0.0  
**Data:** maio/2026

## Produto

Plataforma **100% jurídica** para escritórios de advocacia no Brasil, com camada de **gestão e administração** integrada.

## Incluído

| Domínio | Capacidades |
|---------|-------------|
| Jurídico | Análise documental, CPC, prazos, cálculos, pesquisa, geração de peças |
| Gestão | Workflows, assistente IA, analytics, auditoria multi-tenant |
| Administração | Auth por tenant, rate limit, observabilidade (Sentry, logs JSON), export LGPD |

## Excluído (V2)

- Odontologia, clínicas odontológicas, prontuário odontológico, CRO odontológico
- Qualquer vertical de saúde/medicina fora do contexto jurídico-processual
- Pagamentos Stripe (roadmap futuro, não bloqueia deploy)

## Ontologia

Áreas do direito em `ontology/areas-direito.yaml` — apenas ramos jurídicos brasileiros (civil, trabalhista, penal, tributário, consumidor, família, empresarial, administrativo, previdenciário, constitucional).

## Deploy

Ver `ops/DEPLOY.md` e `ops/GCP-SETUP.md`.
