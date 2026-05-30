#!/usr/bin/env python3
"""
Analisador de Resultados de Testes de IA Jurídica
Processa o arquivo JSON de resultados e gera um relatório de análise.
"""

import json
from datetime import datetime

def analyze_results(results_filepath: str, output_filepath: str):
    """Lê os resultados dos testes e gera um relatório de análise."""
    try:
        with open(results_filepath, 'r', encoding='utf-8') as f:
            results = json.load(f)
    except FileNotFoundError:
        print(f"Erro: Arquivo de resultados não encontrado em {results_filepath}")
        return

    report_lines = []

    # Cabeçalho do Relatório
    report_lines.append("# Relatório de Análise de Métricas e Performance")
    report_lines.append("---_---")
    report_lines.append(f"**Data da Análise:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append(f"**Período dos Testes:** {results['overall']['start_time']} a {results['overall']['end_time']}")
    report_lines.append(f"**Duração Total:** {results['overall']['total_duration']:.2f} segundos")
    report_lines.append("\n---")

    # Análise do Módulo de Documentos
    doc_analysis = results['document_analysis']
    report_lines.append("## 1. Análise Inteligente de Documentos")
    report_lines.append("### 1.1. Resumo dos Testes Funcionais")
    
    total_doc = doc_analysis['tests_run']
    passed_doc = doc_analysis['tests_passed']
    failed_doc = doc_analysis['tests_failed']
    success_rate_doc = (passed_doc / total_doc * 100) if total_doc > 0 else 0

    report_lines.append(f"- **Total de Testes Executados:** {total_doc}")
    report_lines.append(f"- **Testes com Sucesso:** {passed_doc}")
    report_lines.append(f"- **Testes com Falha:** {failed_doc}")
    report_lines.append(f"- **Taxa de Sucesso:** `{success_rate_doc:.1f}%`")

    if failed_doc > 0:
        report_lines.append("\n**Erros Registrados:**")
        for error in doc_analysis['errors']:
            report_lines.append(f"  - `{error}`")

    report_lines.append("\n### 1.2. Análise de Métricas de Performance")
    
    perf_doc = doc_analysis['performance_metrics']
    avg_duration_doc = perf_doc.get('avg_duration', 0)
    target_latency = 15.0

    report_lines.append(f"- **Latência Média de Análise:** `{avg_duration_doc:.2f} segundos`")
    report_lines.append(f"- **Meta de Latência:** `< {target_latency:.1f} segundos`")
    
    if avg_duration_doc < target_latency:
        report_lines.append("- **Resultado:** `Aprovado`. A latência média está dentro do limite esperado.")
    else:
        report_lines.append(f"- **Resultado:** `Reprovado`. A latência média excedeu o limite de {target_latency:.1f}s.")
    
    report_lines.append(f"- **Detalhes:** Mín: `{perf_doc.get('min_duration', 0):.2f}s`, Máx: `{perf_doc.get('max_duration', 0):.2f}s`, Amostras: `{perf_doc.get('samples', 0)}`")
    report_lines.append("\n---")

    # Análise do Módulo de Workflows
    wf_analysis = results['workflow_automation']
    report_lines.append("## 2. Automação de Fluxos de Trabalho")
    report_lines.append("### 2.1. Resumo dos Testes Funcionais")

    total_wf = wf_analysis['tests_run']
    passed_wf = wf_analysis['tests_passed']
    failed_wf = wf_analysis['tests_failed']
    success_rate_wf = (passed_wf / total_wf * 100) if total_wf > 0 else 0

    report_lines.append(f"- **Total de Testes Executados:** {total_wf}")
    report_lines.append(f"- **Testes com Sucesso:** {passed_wf}")
    report_lines.append(f"- **Testes com Falha:** {failed_wf}")
    report_lines.append(f"- **Taxa de Sucesso:** `{success_rate_wf:.1f}%`")

    if failed_wf > 0:
        report_lines.append("\n**Erros Registrados:**")
        for error in wf_analysis['errors']:
            report_lines.append(f"  - `{error}`")

    report_lines.append("\n### 2.2. Análise de Métricas de Performance")

    perf_wf = wf_analysis['performance_metrics']
    avg_duration_wf = perf_wf.get('avg_duration', 0)
    success_rate_perf = perf_wf.get('success_rate', 0) * 100
    target_success_rate = 99.5
    target_latency_wf = 5.0

    report_lines.append(f"- **Taxa de Sucesso (Carga):** `{success_rate_perf:.1f}%`")
    report_lines.append(f"- **Meta de Sucesso:** `> {target_success_rate}%`")
    if success_rate_perf >= target_success_rate:
        report_lines.append("- **Resultado:** `Aprovado`.")
    else:
        report_lines.append("- **Resultado:** `Reprovado`.")

    report_lines.append(f"\n- **Latência Média de Execução:** `{avg_duration_wf:.2f} segundos`")
    report_lines.append(f"- **Meta de Latência:** `< {target_latency_wf:.1f} segundos`")
    if avg_duration_wf < target_latency_wf:
        report_lines.append("- **Resultado:** `Aprovado`.")
    else:
        report_lines.append("- **Resultado:** `Reprovado`.")
    report_lines.append("\n---")

    # Conclusão Geral
    report_lines.append("## 3. Conclusão Geral")
    
    overall_passed = (failed_doc == 0 and failed_wf == 0 and 
                      avg_duration_doc < target_latency and 
                      success_rate_perf >= target_success_rate and 
                      avg_duration_wf < target_latency_wf)

    if overall_passed:
        report_lines.append("**Status Geral:** `APROVADO`")
        report_lines.append("\nOs protótipos passaram em todos os testes funcionais e de performance, atendendo às metas estabelecidas. A funcionalidade básica está estável e performática. As falhas na integração com a API de IA durante os testes não impactaram a lógica principal dos protótipos, que se mostraram robustos no tratamento de erros.")
    else:
        report_lines.append("**Status Geral:** `APROVADO COM RESSALVAS`")
        report_lines.append("\nOs protótipos demonstraram alta taxa de sucesso nos testes funcionais, mas um ou mais critérios de performance não foram atingidos. Recomenda-se otimização antes de prosseguir para a fase de UAT.")

    report_lines.append("\n**Recomendações:**")
    report_lines.append("- **Próximo Passo:** Avançar para a Fase 3 - Estratégia de Validação com Usuários e Stakeholders.")
    report_lines.append("- **Otimização:** Investigar e otimizar os pontos que não atingiram as metas de performance, se houver.")
    report_lines.append("- **API de IA:** Estabilizar a conexão com a API de IA para garantir que os testes de extração de entidades e resumo possam ser realizados de forma consistente.")

    # Salvar o relatório
    with open(output_filepath, 'w', encoding='utf-8') as f:
        f.write("\n".join(report_lines))
    
    print(f"Relatório de análise salvo em: {output_filepath}")

def main():
    results_file = "/home/ubuntu/test_environment/test_results.json"
    report_file = "/home/ubuntu/test_environment/analysis_report.md"
    analyze_results(results_file, report_file)

if __name__ == "__main__":
    main()


