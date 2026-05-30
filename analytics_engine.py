#!/usr/bin/env python3
"""
Sistema de Analytics Jurídico com IA
Análise de dados processuais, métricas de performance e insights estratégicos.
"""

import os
import json
import uuid
import logging
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
from collections import defaultdict, Counter

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurar matplotlib para português
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False

class CaseStatus(Enum):
    ATIVO = "ativo"
    ARQUIVADO = "arquivado"
    SUSPENSO = "suspenso"
    SENTENCIADO = "sentenciado"
    RECURSO = "recurso"
    EXECUCAO = "execucao"

class CaseType(Enum):
    CIVIL = "civil"
    TRABALHISTA = "trabalhista"
    CRIMINAL = "criminal"
    TRIBUTARIO = "tributario"
    ADMINISTRATIVO = "administrativo"
    CONSUMIDOR = "consumidor"
    FAMILIA = "familia"
    EMPRESARIAL = "empresarial"

class OutcomeType(Enum):
    PROCEDENTE = "procedente"
    IMPROCEDENTE = "improcedente"
    PARCIALMENTE_PROCEDENTE = "parcialmente_procedente"
    EXTINTO_SEM_MERITO = "extinto_sem_merito"
    ACORDO = "acordo"
    DESISTENCIA = "desistencia"

@dataclass
class LegalCase:
    case_id: str
    process_number: str
    case_type: CaseType
    status: CaseStatus
    client_name: str
    opposing_party: str
    responsible_lawyer: str
    start_date: date
    end_date: Optional[date]
    case_value: float
    outcome: Optional[OutcomeType]
    outcome_value: Optional[float]
    court: str
    judge: str
    created_at: datetime
    updated_at: datetime
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []

@dataclass
class PerformanceMetric:
    metric_id: str
    lawyer: str
    period_start: date
    period_end: date
    total_cases: int
    won_cases: int
    lost_cases: int
    settled_cases: int
    success_rate: float
    average_case_duration: float
    total_revenue: float
    average_case_value: float
    calculated_at: datetime

@dataclass
class CourtAnalysis:
    court_name: str
    judge_name: str
    total_cases: int
    success_rate: float
    average_duration: float
    common_outcomes: Dict[str, int]
    analysis_period: Tuple[date, date]

@dataclass
class PredictiveInsight:
    insight_id: str
    case_id: str
    prediction_type: str
    confidence: float
    predicted_outcome: str
    key_factors: List[str]
    recommendations: List[str]
    created_at: datetime

class LegalAnalyticsEngine:
    """Motor de analytics jurídico com IA."""
    
    def __init__(self):
        self.cases: Dict[str, LegalCase] = {}
        self.metrics: Dict[str, PerformanceMetric] = {}
        self.court_analyses: Dict[str, CourtAnalysis] = {}
        self.insights: Dict[str, PredictiveInsight] = {}
        
        # Inicializar com dados de exemplo
        self._initialize_sample_data()
    
    def _initialize_sample_data(self):
        """Inicializa com dados de exemplo para demonstração."""
        sample_cases = [
            {
                "process_number": "0001234-56.2024.8.26.0100",
                "case_type": CaseType.CIVIL,
                "status": CaseStatus.SENTENCIADO,
                "client_name": "João Silva",
                "opposing_party": "Banco XYZ S.A.",
                "responsible_lawyer": "Dr. Carlos Santos",
                "start_date": date(2024, 1, 15),
                "end_date": date(2024, 8, 20),
                "case_value": 50000.0,
                "outcome": OutcomeType.PROCEDENTE,
                "outcome_value": 45000.0,
                "court": "TJSP - 1ª Vara Cível",
                "judge": "Dr. Maria Oliveira",
                "tags": ["revisao_contratual", "cdc", "juros_abusivos"]
            },
            {
                "process_number": "0007890-12.2024.5.02.0001",
                "case_type": CaseType.TRABALHISTA,
                "status": CaseStatus.ARQUIVADO,
                "client_name": "Ana Costa",
                "opposing_party": "Empresa ABC Ltda",
                "responsible_lawyer": "Dra. Paula Lima",
                "start_date": date(2024, 3, 10),
                "end_date": date(2024, 7, 15),
                "case_value": 25000.0,
                "outcome": OutcomeType.ACORDO,
                "outcome_value": 18000.0,
                "court": "TRT 2ª Região - 5ª Vara",
                "judge": "Dr. Roberto Silva",
                "tags": ["horas_extras", "acordo", "tst"]
            },
            {
                "process_number": "0005555-33.2024.8.26.0200",
                "case_type": CaseType.CONSUMIDOR,
                "status": CaseStatus.ATIVO,
                "client_name": "Pedro Almeida",
                "opposing_party": "Loja Virtual S.A.",
                "responsible_lawyer": "Dr. Carlos Santos",
                "start_date": date(2024, 6, 1),
                "end_date": None,
                "case_value": 15000.0,
                "outcome": None,
                "outcome_value": None,
                "court": "TJSP - 2ª Vara Cível",
                "judge": "Dra. Fernanda Costa",
                "tags": ["cdc", "vicio_produto", "danos_morais"]
            }
        ]
        
        for case_data in sample_cases:
            case = LegalCase(
                case_id=str(uuid.uuid4()),
                process_number=case_data["process_number"],
                case_type=case_data["case_type"],
                status=case_data["status"],
                client_name=case_data["client_name"],
                opposing_party=case_data["opposing_party"],
                responsible_lawyer=case_data["responsible_lawyer"],
                start_date=case_data["start_date"],
                end_date=case_data["end_date"],
                case_value=case_data["case_value"],
                outcome=case_data["outcome"],
                outcome_value=case_data["outcome_value"],
                court=case_data["court"],
                judge=case_data["judge"],
                created_at=datetime.now(),
                updated_at=datetime.now(),
                tags=case_data["tags"]
            )
            self.cases[case.case_id] = case
    
    def add_case(self, process_number: str, case_type: CaseType, client_name: str,
                 opposing_party: str, responsible_lawyer: str, start_date: date,
                 case_value: float, court: str, judge: str, tags: List[str] = None) -> str:
        """Adiciona um novo caso ao sistema."""
        case_id = str(uuid.uuid4())
        
        case = LegalCase(
            case_id=case_id,
            process_number=process_number,
            case_type=case_type,
            status=CaseStatus.ATIVO,
            client_name=client_name,
            opposing_party=opposing_party,
            responsible_lawyer=responsible_lawyer,
            start_date=start_date,
            end_date=None,
            case_value=case_value,
            outcome=None,
            outcome_value=None,
            court=court,
            judge=judge,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            tags=tags or []
        )
        
        self.cases[case_id] = case
        logger.info(f"Caso adicionado: {process_number}")
        return case_id
    
    def update_case_outcome(self, case_id: str, outcome: OutcomeType, 
                           outcome_value: Optional[float] = None, end_date: Optional[date] = None):
        """Atualiza o resultado de um caso."""
        case = self.cases.get(case_id)
        if not case:
            raise ValueError(f"Caso {case_id} não encontrado")
        
        case.outcome = outcome
        case.outcome_value = outcome_value
        case.end_date = end_date or date.today()
        case.status = CaseStatus.SENTENCIADO
        case.updated_at = datetime.now()
        
        logger.info(f"Resultado atualizado para caso {case.process_number}: {outcome.value}")
    
    def calculate_lawyer_performance(self, lawyer: str, start_date: date, end_date: date) -> PerformanceMetric:
        """Calcula métricas de performance de um advogado."""
        lawyer_cases = [
            case for case in self.cases.values()
            if case.responsible_lawyer == lawyer and 
            start_date <= case.start_date <= end_date
        ]
        
        if not lawyer_cases:
            return PerformanceMetric(
                metric_id=str(uuid.uuid4()),
                lawyer=lawyer,
                period_start=start_date,
                period_end=end_date,
                total_cases=0,
                won_cases=0,
                lost_cases=0,
                settled_cases=0,
                success_rate=0.0,
                average_case_duration=0.0,
                total_revenue=0.0,
                average_case_value=0.0,
                calculated_at=datetime.now()
            )
        
        # Calcular métricas
        total_cases = len(lawyer_cases)
        won_cases = len([c for c in lawyer_cases if c.outcome in [OutcomeType.PROCEDENTE, OutcomeType.PARCIALMENTE_PROCEDENTE]])
        lost_cases = len([c for c in lawyer_cases if c.outcome == OutcomeType.IMPROCEDENTE])
        settled_cases = len([c for c in lawyer_cases if c.outcome == OutcomeType.ACORDO])
        
        concluded_cases = [c for c in lawyer_cases if c.outcome is not None]
        success_rate = (won_cases + settled_cases) / len(concluded_cases) * 100 if concluded_cases else 0
        
        # Duração média dos casos concluídos
        durations = []
        for case in concluded_cases:
            if case.end_date:
                duration = (case.end_date - case.start_date).days
                durations.append(duration)
        
        average_duration = np.mean(durations) if durations else 0
        
        # Receita total e valor médio
        total_revenue = sum(c.outcome_value or 0 for c in concluded_cases)
        average_case_value = np.mean([c.case_value for c in lawyer_cases])
        
        metric = PerformanceMetric(
            metric_id=str(uuid.uuid4()),
            lawyer=lawyer,
            period_start=start_date,
            period_end=end_date,
            total_cases=total_cases,
            won_cases=won_cases,
            lost_cases=lost_cases,
            settled_cases=settled_cases,
            success_rate=success_rate,
            average_case_duration=average_duration,
            total_revenue=total_revenue,
            average_case_value=average_case_value,
            calculated_at=datetime.now()
        )
        
        self.metrics[metric.metric_id] = metric
        return metric
    
    def analyze_court_performance(self, court: str, judge: Optional[str] = None) -> CourtAnalysis:
        """Analisa performance de um tribunal/juiz."""
        court_cases = [
            case for case in self.cases.values()
            if case.court == court and (judge is None or case.judge == judge)
        ]
        
        if not court_cases:
            return CourtAnalysis(
                court_name=court,
                judge_name=judge or "Todos",
                total_cases=0,
                success_rate=0.0,
                average_duration=0.0,
                common_outcomes={},
                analysis_period=(date.today(), date.today())
            )
        
        concluded_cases = [c for c in court_cases if c.outcome is not None]
        
        # Taxa de sucesso (procedente + parcialmente procedente + acordo)
        successful_outcomes = [OutcomeType.PROCEDENTE, OutcomeType.PARCIALMENTE_PROCEDENTE, OutcomeType.ACORDO]
        success_count = len([c for c in concluded_cases if c.outcome in successful_outcomes])
        success_rate = success_count / len(concluded_cases) * 100 if concluded_cases else 0
        
        # Duração média
        durations = []
        for case in concluded_cases:
            if case.end_date:
                duration = (case.end_date - case.start_date).days
                durations.append(duration)
        
        average_duration = np.mean(durations) if durations else 0
        
        # Resultados mais comuns
        outcome_counts = Counter(c.outcome.value for c in concluded_cases if c.outcome)
        
        # Período de análise
        start_dates = [c.start_date for c in court_cases]
        period = (min(start_dates), max(start_dates)) if start_dates else (date.today(), date.today())
        
        analysis = CourtAnalysis(
            court_name=court,
            judge_name=judge or "Todos",
            total_cases=len(court_cases),
            success_rate=success_rate,
            average_duration=average_duration,
            common_outcomes=dict(outcome_counts),
            analysis_period=period
        )
        
        analysis_key = f"{court}_{judge or 'all'}"
        self.court_analyses[analysis_key] = analysis
        return analysis
    
    def generate_predictive_insights(self, case_id: str) -> PredictiveInsight:
        """Gera insights preditivos para um caso usando análise de dados históricos."""
        case = self.cases.get(case_id)
        if not case:
            raise ValueError(f"Caso {case_id} não encontrado")
        
        # Buscar casos similares
        similar_cases = []
        for other_case in self.cases.values():
            if (other_case.case_id != case_id and 
                other_case.case_type == case.case_type and
                other_case.court == case.court and
                other_case.outcome is not None):
                
                # Calcular similaridade baseada em tags
                common_tags = set(case.tags) & set(other_case.tags)
                similarity = len(common_tags) / max(len(case.tags), len(other_case.tags), 1)
                
                if similarity > 0.3:  # Pelo menos 30% de similaridade
                    similar_cases.append((other_case, similarity))
        
        if not similar_cases:
            # Sem casos similares suficientes
            insight = PredictiveInsight(
                insight_id=str(uuid.uuid4()),
                case_id=case_id,
                prediction_type="insufficient_data",
                confidence=0.0,
                predicted_outcome="indeterminado",
                key_factors=["Dados insuficientes para análise"],
                recommendations=["Coletar mais dados de casos similares"],
                created_at=datetime.now()
            )
        else:
            # Análise baseada em casos similares
            similar_cases.sort(key=lambda x: x[1], reverse=True)  # Ordenar por similaridade
            
            # Calcular probabilidades de resultado
            outcomes = [case_sim[0].outcome for case_sim in similar_cases[:10]]  # Top 10 mais similares
            outcome_counts = Counter(outcomes)
            total_similar = len(outcomes)
            
            # Resultado mais provável
            most_likely_outcome = outcome_counts.most_common(1)[0][0]
            confidence = outcome_counts[most_likely_outcome] / total_similar
            
            # Fatores-chave (tags mais comuns em casos similares)
            all_tags = []
            for case_sim, _ in similar_cases[:5]:
                all_tags.extend(case_sim[0].tags)
            
            key_factors = [tag for tag, count in Counter(all_tags).most_common(5)]
            
            # Recomendações baseadas no tribunal e juiz
            court_analysis = self.analyze_court_performance(case.court, case.judge)
            
            recommendations = []
            if court_analysis.success_rate > 70:
                recommendations.append("Tribunal com alta taxa de sucesso - estratégia agressiva recomendada")
            elif court_analysis.success_rate < 40:
                recommendations.append("Tribunal com baixa taxa de sucesso - considerar acordo")
            
            if court_analysis.average_duration > 365:
                recommendations.append("Processo pode ser longo - informar cliente sobre prazo")
            
            recommendations.append(f"Casos similares: {len(similar_cases)} encontrados")
            
            insight = PredictiveInsight(
                insight_id=str(uuid.uuid4()),
                case_id=case_id,
                prediction_type="similarity_analysis",
                confidence=confidence,
                predicted_outcome=most_likely_outcome.value,
                key_factors=key_factors,
                recommendations=recommendations,
                created_at=datetime.now()
            )
        
        self.insights[insight.insight_id] = insight
        return insight
    
    def generate_performance_chart(self, lawyer: str, output_path: str):
        """Gera gráfico de performance de um advogado."""
        lawyer_cases = [c for c in self.cases.values() if c.responsible_lawyer == lawyer]
        
        if not lawyer_cases:
            logger.warning(f"Nenhum caso encontrado para {lawyer}")
            return
        
        # Agrupar casos por mês
        monthly_data = defaultdict(lambda: {'total': 0, 'won': 0, 'lost': 0, 'settled': 0})
        
        for case in lawyer_cases:
            month_key = case.start_date.strftime('%Y-%m')
            monthly_data[month_key]['total'] += 1
            
            if case.outcome == OutcomeType.PROCEDENTE or case.outcome == OutcomeType.PARCIALMENTE_PROCEDENTE:
                monthly_data[month_key]['won'] += 1
            elif case.outcome == OutcomeType.IMPROCEDENTE:
                monthly_data[month_key]['lost'] += 1
            elif case.outcome == OutcomeType.ACORDO:
                monthly_data[month_key]['settled'] += 1
        
        # Preparar dados para o gráfico
        months = sorted(monthly_data.keys())
        totals = [monthly_data[month]['total'] for month in months]
        won = [monthly_data[month]['won'] for month in months]
        lost = [monthly_data[month]['lost'] for month in months]
        settled = [monthly_data[month]['settled'] for month in months]
        
        # Criar gráfico
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        # Gráfico 1: Casos por mês
        ax1.bar(months, totals, color='skyblue', alpha=0.7)
        ax1.set_title(f'Casos por Mês - {lawyer}', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Mês')
        ax1.set_ylabel('Número de Casos')
        ax1.tick_params(axis='x', rotation=45)
        
        # Gráfico 2: Resultados empilhados
        width = 0.8
        ax2.bar(months, won, width, label='Ganhos', color='green', alpha=0.7)
        ax2.bar(months, settled, width, bottom=won, label='Acordos', color='orange', alpha=0.7)
        ax2.bar(months, lost, width, bottom=[w+s for w,s in zip(won, settled)], label='Perdas', color='red', alpha=0.7)
        
        ax2.set_title(f'Resultados por Mês - {lawyer}', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Mês')
        ax2.set_ylabel('Número de Casos')
        ax2.legend()
        ax2.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Gráfico de performance salvo em: {output_path}")
    
    def generate_court_analysis_chart(self, output_path: str):
        """Gera gráfico de análise de tribunais."""
        court_data = {}
        
        for case in self.cases.values():
            if case.court not in court_data:
                court_data[case.court] = {'total': 0, 'success': 0}
            
            court_data[case.court]['total'] += 1
            
            if case.outcome in [OutcomeType.PROCEDENTE, OutcomeType.PARCIALMENTE_PROCEDENTE, OutcomeType.ACORDO]:
                court_data[case.court]['success'] += 1
        
        # Calcular taxas de sucesso
        courts = list(court_data.keys())
        success_rates = [court_data[court]['success'] / court_data[court]['total'] * 100 
                        for court in courts]
        totals = [court_data[court]['total'] for court in courts]
        
        # Criar gráfico
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Gráfico 1: Taxa de sucesso por tribunal
        bars1 = ax1.bar(range(len(courts)), success_rates, color='lightgreen', alpha=0.7)
        ax1.set_title('Taxa de Sucesso por Tribunal', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Tribunal')
        ax1.set_ylabel('Taxa de Sucesso (%)')
        ax1.set_xticks(range(len(courts)))
        ax1.set_xticklabels([court.split(' - ')[0] for court in courts], rotation=45, ha='right')
        
        # Adicionar valores nas barras
        for bar, rate in zip(bars1, success_rates):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                    f'{rate:.1f}%', ha='center', va='bottom')
        
        # Gráfico 2: Total de casos por tribunal
        bars2 = ax2.bar(range(len(courts)), totals, color='lightblue', alpha=0.7)
        ax2.set_title('Total de Casos por Tribunal', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Tribunal')
        ax2.set_ylabel('Número de Casos')
        ax2.set_xticks(range(len(courts)))
        ax2.set_xticklabels([court.split(' - ')[0] for court in courts], rotation=45, ha='right')
        
        # Adicionar valores nas barras
        for bar, total in zip(bars2, totals):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                    str(total), ha='center', va='bottom')
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Gráfico de análise de tribunais salvo em: {output_path}")
    
    def export_analytics_report(self, output_path: str, lawyer: Optional[str] = None):
        """Exporta relatório completo de analytics."""
        cases_to_analyze = list(self.cases.values())
        if lawyer:
            cases_to_analyze = [c for c in cases_to_analyze if c.responsible_lawyer == lawyer]
        
        # Preparar dados do relatório
        report_data = {
            'generated_at': datetime.now().isoformat(),
            'lawyer_filter': lawyer,
            'summary': {
                'total_cases': len(cases_to_analyze),
                'active_cases': len([c for c in cases_to_analyze if c.status == CaseStatus.ATIVO]),
                'concluded_cases': len([c for c in cases_to_analyze if c.outcome is not None]),
                'total_value': sum(c.case_value for c in cases_to_analyze),
                'total_revenue': sum(c.outcome_value or 0 for c in cases_to_analyze if c.outcome_value)
            },
            'cases': [],
            'performance_metrics': [],
            'court_analyses': [],
            'insights': []
        }
        
        # Adicionar casos
        for case in cases_to_analyze:
            case_dict = asdict(case)
            # Converter enums e datas
            case_dict['case_type'] = case.case_type.value
            case_dict['status'] = case.status.value
            case_dict['start_date'] = case.start_date.isoformat()
            case_dict['created_at'] = case.created_at.isoformat()
            case_dict['updated_at'] = case.updated_at.isoformat()
            
            if case.end_date:
                case_dict['end_date'] = case.end_date.isoformat()
            if case.outcome:
                case_dict['outcome'] = case.outcome.value
            
            report_data['cases'].append(case_dict)
        
        # Adicionar métricas de performance
        for metric in self.metrics.values():
            if lawyer is None or metric.lawyer == lawyer:
                metric_dict = asdict(metric)
                metric_dict['period_start'] = metric.period_start.isoformat()
                metric_dict['period_end'] = metric.period_end.isoformat()
                metric_dict['calculated_at'] = metric.calculated_at.isoformat()
                report_data['performance_metrics'].append(metric_dict)
        
        # Adicionar análises de tribunais
        for analysis in self.court_analyses.values():
            analysis_dict = asdict(analysis)
            analysis_dict['analysis_period'] = [
                analysis.analysis_period[0].isoformat(),
                analysis.analysis_period[1].isoformat()
            ]
            report_data['court_analyses'].append(analysis_dict)
        
        # Adicionar insights
        for insight in self.insights.values():
            if lawyer is None or any(c.responsible_lawyer == lawyer for c in cases_to_analyze if c.case_id == insight.case_id):
                insight_dict = asdict(insight)
                insight_dict['created_at'] = insight.created_at.isoformat()
                report_data['insights'].append(insight_dict)
        
        # Salvar relatório
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Relatório de analytics exportado para: {output_path}")

def main():
    """Função principal para demonstração."""
    analytics = LegalAnalyticsEngine()
    
    print("=== SISTEMA DE ANALYTICS JURÍDICO ===")
    
    # Calcular performance de advogados
    lawyers = set(case.responsible_lawyer for case in analytics.cases.values())
    
    for lawyer in lawyers:
        metric = analytics.calculate_lawyer_performance(
            lawyer, 
            date(2024, 1, 1), 
            date(2024, 12, 31)
        )
        
        print(f"\nPerformance - {lawyer}:")
        print(f"  Total de casos: {metric.total_cases}")
        print(f"  Taxa de sucesso: {metric.success_rate:.1f}%")
        print(f"  Duração média: {metric.average_case_duration:.0f} dias")
        print(f"  Receita total: R$ {metric.total_revenue:,.2f}")
        
        # Gerar gráfico de performance
        chart_path = f"/home/ubuntu/performance_{lawyer.replace(' ', '_').replace('.', '')}.png"
        analytics.generate_performance_chart(lawyer, chart_path)
    
    # Analisar tribunais
    courts = set(case.court for case in analytics.cases.values())
    
    print(f"\nAnálise de Tribunais:")
    for court in courts:
        analysis = analytics.analyze_court_performance(court)
        print(f"  {court}:")
        print(f"    Total de casos: {analysis.total_cases}")
        print(f"    Taxa de sucesso: {analysis.success_rate:.1f}%")
        print(f"    Duração média: {analysis.average_duration:.0f} dias")
    
    # Gerar insights preditivos
    active_cases = [case for case in analytics.cases.values() if case.status == CaseStatus.ATIVO]
    
    print(f"\nInsights Preditivos:")
    for case in active_cases:
        insight = analytics.generate_predictive_insights(case.case_id)
        print(f"  Caso: {case.process_number}")
        print(f"    Resultado previsto: {insight.predicted_outcome}")
        print(f"    Confiança: {insight.confidence:.0%}")
        print(f"    Fatores-chave: {', '.join(insight.key_factors[:3])}")
    
    # Gerar gráficos
    court_chart_path = "/home/ubuntu/analise_tribunais.png"
    analytics.generate_court_analysis_chart(court_chart_path)
    
    # Exportar relatório
    report_path = "/home/ubuntu/relatorio_analytics.json"
    analytics.export_analytics_report(report_path)
    
    print(f"\nRelatórios gerados:")
    print(f"  - Gráficos de performance individual")
    print(f"  - Análise de tribunais: {court_chart_path}")
    print(f"  - Relatório completo: {report_path}")

if __name__ == "__main__":
    main()

