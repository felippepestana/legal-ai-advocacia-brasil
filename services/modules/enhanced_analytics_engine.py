#!/usr/bin/env python3
"""
Sistema de Analytics Jurídico - Versão Melhorada
Implementa melhorias: dashboards mais informativos, análises preditivas avançadas
e relatórios personalizáveis
"""

import json
import os
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _analytics_charts_dir() -> Path:
    """Diretório gravável para PNGs (substitui paths legados /home/ubuntu/...)."""
    raw = os.environ.get("ANALYTICS_CHARTS_DIR", "").strip()
    if raw:
        path = Path(raw)
    else:
        path = Path(__file__).resolve().parents[2] / "data" / "analytics"
    path.mkdir(parents=True, exist_ok=True)
    return path


# Configuração de fontes para gráficos
plt.rcParams['font.family'] = 'DejaVu Sans'
sns.set_style("whitegrid")

class AnalysisType(Enum):
    """Tipos de análise"""
    PERFORMANCE = "Performance"
    PREDICTIVE = "Preditiva"
    COMPARATIVE = "Comparativa"
    TREND = "Tendência"
    FINANCIAL = "Financeira"
    OPERATIONAL = "Operacional"

class MetricType(Enum):
    """Tipos de métricas"""
    SUCCESS_RATE = "Taxa de Sucesso"
    AVERAGE_TIME = "Tempo Médio"
    COST_EFFICIENCY = "Eficiência de Custo"
    CLIENT_SATISFACTION = "Satisfação do Cliente"
    REVENUE = "Receita"
    CASE_VOLUME = "Volume de Casos"

@dataclass
class CaseData:
    """Dados de caso jurídico"""
    id: str
    type: str
    client_id: str
    lawyer_id: str
    start_date: datetime
    end_date: Optional[datetime]
    status: str
    value: float
    outcome: Optional[str]
    duration_days: Optional[int]
    costs: float
    area: str  # Área do direito

@dataclass
class AnalyticsReport:
    """Relatório de analytics"""
    id: str
    title: str
    analysis_type: AnalysisType
    generated_at: datetime
    data_period: Tuple[datetime, datetime]
    metrics: Dict[str, Any]
    insights: List[str]
    recommendations: List[str]
    charts: List[str]  # Caminhos dos gráficos

class DataGenerator:
    """Gerador de dados sintéticos para demonstração"""
    
    def __init__(self):
        self.areas_direito = [
            "Civil", "Trabalhista", "Penal", "Tributário", 
            "Empresarial", "Consumidor", "Família", "Previdenciário"
        ]
        
        self.tipos_caso = {
            "Civil": ["Danos Morais", "Cobrança", "Indenização", "Rescisão Contratual"],
            "Trabalhista": ["Rescisão", "Horas Extras", "Adicional Noturno", "FGTS"],
            "Penal": ["Defesa Criminal", "Habeas Corpus", "Recurso", "Execução Penal"],
            "Tributário": ["Restituição", "Parcelamento", "Defesa Fiscal", "Planejamento"],
            "Empresarial": ["Constituição", "Contratos", "Fusões", "Compliance"],
            "Consumidor": ["Defeito Produto", "Publicidade Enganosa", "Cobrança Indevida"],
            "Família": ["Divórcio", "Pensão", "Guarda", "Inventário"],
            "Previdenciário": ["Aposentadoria", "Auxílio", "Revisão", "Pensão"]
        }
        
        self.status_casos = ["Em Andamento", "Concluído", "Suspenso", "Arquivado"]
        self.outcomes = ["Procedente", "Improcedente", "Parcialmente Procedente", "Acordo"]
    
    def generate_case_data(self, num_cases: int = 1000, 
                          start_date: datetime = None, 
                          end_date: datetime = None) -> List[CaseData]:
        """Gera dados sintéticos de casos"""
        if start_date is None:
            start_date = datetime.now() - timedelta(days=365*2)
        if end_date is None:
            end_date = datetime.now()
        
        cases = []
        
        for i in range(num_cases):
            area = np.random.choice(self.areas_direito)
            tipo = np.random.choice(self.tipos_caso[area])
            
            # Data de início aleatória
            case_start = start_date + timedelta(
                days=np.random.randint(0, (end_date - start_date).days)
            )
            
            # Status e data de fim
            status = np.random.choice(self.status_casos, p=[0.4, 0.45, 0.1, 0.05])
            
            if status == "Concluído":
                duration = np.random.randint(30, 730)  # 30 dias a 2 anos
                case_end = case_start + timedelta(days=duration)
                outcome = np.random.choice(self.outcomes, p=[0.4, 0.2, 0.3, 0.1])
            else:
                duration = (datetime.now() - case_start).days if status == "Em Andamento" else None
                case_end = None
                outcome = None
            
            # Valor do caso baseado na área
            base_values = {
                "Civil": (5000, 100000),
                "Trabalhista": (3000, 50000),
                "Penal": (2000, 30000),
                "Tributário": (10000, 500000),
                "Empresarial": (20000, 1000000),
                "Consumidor": (1000, 20000),
                "Família": (2000, 100000),
                "Previdenciário": (5000, 80000)
            }
            
            min_val, max_val = base_values[area]
            value = np.random.uniform(min_val, max_val)
            
            # Custos (10-30% do valor)
            costs = value * np.random.uniform(0.1, 0.3)
            
            case = CaseData(
                id=f"CASE_{i+1:04d}",
                type=tipo,
                client_id=f"CLIENT_{np.random.randint(1, 500):03d}",
                lawyer_id=f"LAWYER_{np.random.randint(1, 20):02d}",
                start_date=case_start,
                end_date=case_end,
                status=status,
                value=value,
                outcome=outcome,
                duration_days=duration,
                costs=costs,
                area=area
            )
            
            cases.append(case)
        
        return cases

class EnhancedAnalyticsEngine:
    """Motor de analytics aprimorado"""
    
    def __init__(self):
        self.data_generator = DataGenerator()
        self.case_data = []
        self.reports = {}
    
    def load_data(self, cases: List[CaseData] = None):
        """Carrega dados de casos"""
        if cases is None:
            logger.info("Gerando dados sintéticos...")
            self.case_data = self.data_generator.generate_case_data(1000)
        else:
            self.case_data = cases
        
        logger.info(f"Dados carregados: {len(self.case_data)} casos")
    
    def generate_performance_analysis(self) -> AnalyticsReport:
        """Gera análise de performance"""
        logger.info("Gerando análise de performance...")
        
        df = pd.DataFrame([asdict(case) for case in self.case_data])
        
        # Métricas de performance
        metrics = {}
        
        # Taxa de sucesso por área
        concluded_cases = df[df['status'] == 'Concluído']
        if not concluded_cases.empty:
            success_rate_by_area = concluded_cases.groupby('area')['outcome'].apply(
                lambda x: (x.isin(['Procedente', 'Parcialmente Procedente', 'Acordo']).sum() / len(x)) * 100
            ).to_dict()
            metrics['success_rate_by_area'] = success_rate_by_area
            metrics['overall_success_rate'] = concluded_cases['outcome'].apply(
                lambda x: x in ['Procedente', 'Parcialmente Procedente', 'Acordo']
            ).mean() * 100
        
        # Tempo médio por área
        if not concluded_cases.empty:
            avg_duration_by_area = concluded_cases.groupby('area')['duration_days'].mean().to_dict()
            metrics['avg_duration_by_area'] = avg_duration_by_area
            metrics['overall_avg_duration'] = concluded_cases['duration_days'].mean()
        
        # Volume de casos por mês
        df['start_month'] = pd.to_datetime(df['start_date']).dt.to_period('M')
        monthly_volume = df.groupby('start_month').size().to_dict()
        metrics['monthly_volume'] = {str(k): v for k, v in monthly_volume.items()}
        
        # Receita por área
        revenue_by_area = df.groupby('area')['value'].sum().to_dict()
        metrics['revenue_by_area'] = revenue_by_area
        metrics['total_revenue'] = df['value'].sum()
        
        # Eficiência de custo
        df['profit_margin'] = ((df['value'] - df['costs']) / df['value']) * 100
        cost_efficiency_by_area = df.groupby('area')['profit_margin'].mean().to_dict()
        metrics['cost_efficiency_by_area'] = cost_efficiency_by_area
        
        # Gera gráficos
        charts = self._generate_performance_charts(df, metrics)
        
        # Insights
        insights = self._generate_performance_insights(metrics)
        
        # Recomendações
        recommendations = self._generate_performance_recommendations(metrics)
        
        report = AnalyticsReport(
            id=f"performance_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            title="Análise de Performance Jurídica",
            analysis_type=AnalysisType.PERFORMANCE,
            generated_at=datetime.now(),
            data_period=(df['start_date'].min(), df['start_date'].max()),
            metrics=metrics,
            insights=insights,
            recommendations=recommendations,
            charts=charts
        )
        
        self.reports[report.id] = report
        return report
    
    def generate_predictive_analysis(self) -> AnalyticsReport:
        """Gera análise preditiva"""
        logger.info("Gerando análise preditiva...")
        
        df = pd.DataFrame([asdict(case) for case in self.case_data])
        
        metrics = {}
        
        # Previsão de volume de casos
        df['start_date'] = pd.to_datetime(df['start_date'])
        monthly_data = df.set_index('start_date').resample('M').size()
        
        # Tendência simples (média móvel)
        trend = monthly_data.rolling(window=3).mean().dropna()
        last_trend = trend.iloc[-1] if not trend.empty else 0
        
        # Previsão para próximos 6 meses
        future_months = pd.date_range(
            start=monthly_data.index[-1] + pd.DateOffset(months=1),
            periods=6,
            freq='M'
        )
        
        # Previsão simples baseada na tendência
        growth_rate = 0.05  # 5% de crescimento mensal
        predictions = []
        base_value = last_trend
        
        for i, month in enumerate(future_months):
            predicted_value = base_value * (1 + growth_rate) ** (i + 1)
            predictions.append(predicted_value)
        
        metrics['volume_prediction'] = {
            str(month.date()): pred for month, pred in zip(future_months, predictions)
        }
        
        # Previsão de receita
        avg_case_value = df['value'].mean()
        revenue_predictions = [pred * avg_case_value for pred in predictions]
        metrics['revenue_prediction'] = {
            str(month.date()): pred for month, pred in zip(future_months, revenue_predictions)
        }
        
        # Análise de sazonalidade
        df['month'] = df['start_date'].dt.month
        seasonal_pattern = df.groupby('month').size().to_dict()
        metrics['seasonal_pattern'] = seasonal_pattern
        
        # Probabilidade de sucesso por tipo de caso
        concluded_cases = df[df['status'] == 'Concluído']
        if not concluded_cases.empty:
            success_prob_by_type = concluded_cases.groupby('type')['outcome'].apply(
                lambda x: (x.isin(['Procedente', 'Parcialmente Procedente', 'Acordo']).sum() / len(x))
            ).to_dict()
            metrics['success_probability_by_type'] = success_prob_by_type
        
        # Gera gráficos
        charts = self._generate_predictive_charts(df, metrics)
        
        # Insights
        insights = self._generate_predictive_insights(metrics)
        
        # Recomendações
        recommendations = self._generate_predictive_recommendations(metrics)
        
        report = AnalyticsReport(
            id=f"predictive_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            title="Análise Preditiva Jurídica",
            analysis_type=AnalysisType.PREDICTIVE,
            generated_at=datetime.now(),
            data_period=(df['start_date'].min(), df['start_date'].max()),
            metrics=metrics,
            insights=insights,
            recommendations=recommendations,
            charts=charts
        )
        
        self.reports[report.id] = report
        return report
    
    def generate_financial_analysis(self) -> AnalyticsReport:
        """Gera análise financeira"""
        logger.info("Gerando análise financeira...")
        
        df = pd.DataFrame([asdict(case) for case in self.case_data])
        
        metrics = {}
        
        # Receita total e por período
        df['start_date'] = pd.to_datetime(df['start_date'])
        df['year_month'] = df['start_date'].dt.to_period('M')
        
        monthly_revenue = df.groupby('year_month')['value'].sum().to_dict()
        metrics['monthly_revenue'] = {str(k): v for k, v in monthly_revenue.items()}
        metrics['total_revenue'] = df['value'].sum()
        
        # Custos e margem de lucro
        metrics['total_costs'] = df['costs'].sum()
        metrics['total_profit'] = metrics['total_revenue'] - metrics['total_costs']
        metrics['profit_margin'] = (metrics['total_profit'] / metrics['total_revenue']) * 100
        
        # ROI por área
        roi_by_area = df.groupby('area').apply(
            lambda x: ((x['value'].sum() - x['costs'].sum()) / x['costs'].sum()) * 100
        ).to_dict()
        metrics['roi_by_area'] = roi_by_area
        
        # Ticket médio por área
        avg_ticket_by_area = df.groupby('area')['value'].mean().to_dict()
        metrics['avg_ticket_by_area'] = avg_ticket_by_area
        
        # Análise de concentração de receita
        revenue_concentration = df.groupby('area')['value'].sum().sort_values(ascending=False)
        top_3_areas = revenue_concentration.head(3)
        metrics['revenue_concentration'] = {
            'top_3_areas': top_3_areas.to_dict(),
            'top_3_percentage': (top_3_areas.sum() / revenue_concentration.sum()) * 100
        }
        
        # Gera gráficos
        charts = self._generate_financial_charts(df, metrics)
        
        # Insights
        insights = self._generate_financial_insights(metrics)
        
        # Recomendações
        recommendations = self._generate_financial_recommendations(metrics)
        
        report = AnalyticsReport(
            id=f"financial_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            title="Análise Financeira Jurídica",
            analysis_type=AnalysisType.FINANCIAL,
            generated_at=datetime.now(),
            data_period=(df['start_date'].min(), df['start_date'].max()),
            metrics=metrics,
            insights=insights,
            recommendations=recommendations,
            charts=charts
        )
        
        self.reports[report.id] = report
        return report
    
    def _generate_performance_charts(self, df: pd.DataFrame, metrics: Dict[str, Any]) -> List[str]:
        """Gera gráficos de performance"""
        charts = []
        
        # Gráfico 1: Taxa de sucesso por área
        if 'success_rate_by_area' in metrics:
            fig, ax = plt.subplots(figsize=(12, 6))
            areas = list(metrics['success_rate_by_area'].keys())
            rates = list(metrics['success_rate_by_area'].values())
            
            bars = ax.bar(areas, rates, color='skyblue', edgecolor='navy', alpha=0.7)
            ax.set_title('Taxa de Sucesso por Área do Direito', fontsize=14, fontweight='bold')
            ax.set_ylabel('Taxa de Sucesso (%)')
            ax.set_xlabel('Área do Direito')
            plt.xticks(rotation=45)
            
            # Adiciona valores nas barras
            for bar, rate in zip(bars, rates):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                       f'{rate:.1f}%', ha='center', va='bottom')
            
            plt.tight_layout()
            chart_path = str(_analytics_charts_dir() / "success_rate_by_area.png")
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            charts.append(chart_path)
        
        # Gráfico 2: Volume de casos por mês
        if 'monthly_volume' in metrics:
            fig, ax = plt.subplots(figsize=(14, 6))
            months = list(metrics['monthly_volume'].keys())
            volumes = list(metrics['monthly_volume'].values())
            
            ax.plot(months, volumes, marker='o', linewidth=2, markersize=6, color='green')
            ax.set_title('Volume de Casos por Mês', fontsize=14, fontweight='bold')
            ax.set_ylabel('Número de Casos')
            ax.set_xlabel('Mês')
            plt.xticks(rotation=45)
            ax.grid(True, alpha=0.3)
            
            plt.tight_layout()
            chart_path = str(_analytics_charts_dir() / "monthly_volume.png")
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            charts.append(chart_path)
        
        # Gráfico 3: Receita por área
        if 'revenue_by_area' in metrics:
            fig, ax = plt.subplots(figsize=(10, 8))
            areas = list(metrics['revenue_by_area'].keys())
            revenues = list(metrics['revenue_by_area'].values())
            
            colors = plt.cm.Set3(np.linspace(0, 1, len(areas)))
            wedges, texts, autotexts = ax.pie(revenues, labels=areas, autopct='%1.1f%%',
                                            colors=colors, startangle=90)
            ax.set_title('Distribuição de Receita por Área', fontsize=14, fontweight='bold')
            
            plt.tight_layout()
            chart_path = str(_analytics_charts_dir() / "revenue_by_area.png")
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            charts.append(chart_path)
        
        return charts
    
    def _generate_predictive_charts(self, df: pd.DataFrame, metrics: Dict[str, Any]) -> List[str]:
        """Gera gráficos preditivos"""
        charts = []
        
        # Gráfico de previsão de volume
        if 'volume_prediction' in metrics:
            fig, ax = plt.subplots(figsize=(14, 6))
            
            # Dados históricos
            df['start_date'] = pd.to_datetime(df['start_date'])
            historical = df.set_index('start_date').resample('M').size()
            
            # Dados de previsão
            pred_dates = list(metrics['volume_prediction'].keys())
            pred_values = list(metrics['volume_prediction'].values())
            
            # Plot histórico
            ax.plot(historical.index, historical.values, 'o-', label='Histórico', 
                   color='blue', linewidth=2)
            
            # Plot previsão
            pred_dates_dt = pd.to_datetime(pred_dates)
            ax.plot(pred_dates_dt, pred_values, 's--', label='Previsão', 
                   color='red', linewidth=2, alpha=0.7)
            
            ax.set_title('Previsão de Volume de Casos', fontsize=14, fontweight='bold')
            ax.set_ylabel('Número de Casos')
            ax.set_xlabel('Período')
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            plt.tight_layout()
            chart_path = str(_analytics_charts_dir() / "volume_prediction.png")
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            charts.append(chart_path)
        
        return charts
    
    def _generate_financial_charts(self, df: pd.DataFrame, metrics: Dict[str, Any]) -> List[str]:
        """Gera gráficos financeiros"""
        charts = []
        
        # Gráfico de receita mensal
        if 'monthly_revenue' in metrics:
            fig, ax = plt.subplots(figsize=(14, 6))
            months = list(metrics['monthly_revenue'].keys())
            revenues = list(metrics['monthly_revenue'].values())
            
            ax.bar(months, revenues, color='gold', edgecolor='orange', alpha=0.8)
            ax.set_title('Receita Mensal', fontsize=14, fontweight='bold')
            ax.set_ylabel('Receita (R$)')
            ax.set_xlabel('Mês')
            plt.xticks(rotation=45)
            
            # Formata valores em milhares
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'R$ {x/1000:.0f}K'))
            
            plt.tight_layout()
            chart_path = str(_analytics_charts_dir() / "monthly_revenue.png")
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            charts.append(chart_path)
        
        return charts
    
    def _generate_performance_insights(self, metrics: Dict[str, Any]) -> List[str]:
        """Gera insights de performance"""
        insights = []
        
        if 'overall_success_rate' in metrics:
            rate = metrics['overall_success_rate']
            if rate > 70:
                insights.append(f"Excelente taxa de sucesso geral de {rate:.1f}%, indicando alta qualidade dos serviços.")
            elif rate > 50:
                insights.append(f"Taxa de sucesso moderada de {rate:.1f}%, com potencial para melhoria.")
            else:
                insights.append(f"Taxa de sucesso baixa de {rate:.1f}%, requer atenção imediata.")
        
        if 'success_rate_by_area' in metrics:
            best_area = max(metrics['success_rate_by_area'], key=metrics['success_rate_by_area'].get)
            worst_area = min(metrics['success_rate_by_area'], key=metrics['success_rate_by_area'].get)
            insights.append(f"Área com melhor performance: {best_area} ({metrics['success_rate_by_area'][best_area]:.1f}%)")
            insights.append(f"Área que precisa de atenção: {worst_area} ({metrics['success_rate_by_area'][worst_area]:.1f}%)")
        
        if 'overall_avg_duration' in metrics:
            duration = metrics['overall_avg_duration']
            insights.append(f"Tempo médio de resolução: {duration:.0f} dias")
        
        return insights
    
    def _generate_predictive_insights(self, metrics: Dict[str, Any]) -> List[str]:
        """Gera insights preditivos"""
        insights = []
        
        if 'volume_prediction' in metrics:
            current_month = list(metrics['volume_prediction'].values())[0]
            last_month = list(metrics['volume_prediction'].values())[-1]
            growth = ((last_month - current_month) / current_month) * 100
            insights.append(f"Previsão de crescimento de {growth:.1f}% no volume de casos nos próximos 6 meses")
        
        if 'seasonal_pattern' in metrics:
            peak_month = max(metrics['seasonal_pattern'], key=metrics['seasonal_pattern'].get)
            low_month = min(metrics['seasonal_pattern'], key=metrics['seasonal_pattern'].get)
            months = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 
                     'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
            insights.append(f"Pico sazonal em {months[peak_month-1]}, menor volume em {months[low_month-1]}")
        
        return insights
    
    def _generate_financial_insights(self, metrics: Dict[str, Any]) -> List[str]:
        """Gera insights financeiros"""
        insights = []
        
        if 'profit_margin' in metrics:
            margin = metrics['profit_margin']
            if margin > 30:
                insights.append(f"Excelente margem de lucro de {margin:.1f}%")
            elif margin > 15:
                insights.append(f"Margem de lucro saudável de {margin:.1f}%")
            else:
                insights.append(f"Margem de lucro baixa de {margin:.1f}%, requer otimização")
        
        if 'revenue_concentration' in metrics:
            concentration = metrics['revenue_concentration']['top_3_percentage']
            insights.append(f"Top 3 áreas concentram {concentration:.1f}% da receita")
        
        return insights
    
    def _generate_performance_recommendations(self, metrics: Dict[str, Any]) -> List[str]:
        """Gera recomendações de performance"""
        recommendations = []
        
        if 'success_rate_by_area' in metrics:
            worst_area = min(metrics['success_rate_by_area'], key=metrics['success_rate_by_area'].get)
            worst_rate = metrics['success_rate_by_area'][worst_area]
            if worst_rate < 50:
                recommendations.append(f"Revisar estratégias na área de {worst_area} (taxa de sucesso: {worst_rate:.1f}%)")
        
        if 'avg_duration_by_area' in metrics:
            slowest_area = max(metrics['avg_duration_by_area'], key=metrics['avg_duration_by_area'].get)
            recommendations.append(f"Otimizar processos na área de {slowest_area} para reduzir tempo de resolução")
        
        recommendations.append("Implementar sistema de acompanhamento de KPIs em tempo real")
        recommendations.append("Estabelecer metas específicas por área do direito")
        
        return recommendations
    
    def _generate_predictive_recommendations(self, metrics: Dict[str, Any]) -> List[str]:
        """Gera recomendações preditivas"""
        recommendations = []
        
        recommendations.append("Preparar recursos para aumento previsto na demanda")
        recommendations.append("Desenvolver estratégias sazonais baseadas nos padrões identificados")
        recommendations.append("Investir em automação para lidar com maior volume de casos")
        recommendations.append("Monitorar tendências mensalmente para ajustar previsões")
        
        return recommendations
    
    def _generate_financial_recommendations(self, metrics: Dict[str, Any]) -> List[str]:
        """Gera recomendações financeiras"""
        recommendations = []
        
        if 'profit_margin' in metrics and metrics['profit_margin'] < 20:
            recommendations.append("Revisar estrutura de custos para melhorar margem de lucro")
        
        if 'revenue_concentration' in metrics:
            concentration = metrics['revenue_concentration']['top_3_percentage']
            if concentration > 70:
                recommendations.append("Diversificar portfólio para reduzir dependência de poucas áreas")
        
        recommendations.append("Implementar sistema de controle de custos por caso")
        recommendations.append("Estabelecer metas de rentabilidade por área")
        
        return recommendations
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Retorna dados para dashboard"""
        if not self.case_data:
            return {"error": "Nenhum dado carregado"}
        
        df = pd.DataFrame([asdict(case) for case in self.case_data])
        
        # KPIs principais
        total_cases = len(df)
        active_cases = len(df[df['status'] == 'Em Andamento'])
        concluded_cases = len(df[df['status'] == 'Concluído'])
        total_revenue = df['value'].sum()
        
        # Taxa de sucesso
        concluded_df = df[df['status'] == 'Concluído']
        if not concluded_df.empty:
            success_rate = (concluded_df['outcome'].isin(['Procedente', 'Parcialmente Procedente', 'Acordo']).sum() / len(concluded_df)) * 100
        else:
            success_rate = 0
        
        return {
            "kpis": {
                "total_cases": total_cases,
                "active_cases": active_cases,
                "concluded_cases": concluded_cases,
                "success_rate": round(success_rate, 1),
                "total_revenue": total_revenue,
                "avg_case_value": round(df['value'].mean(), 2)
            },
            "charts_data": {
                "cases_by_area": df['area'].value_counts().to_dict(),
                "cases_by_status": df['status'].value_counts().to_dict(),
                "revenue_by_area": df.groupby('area')['value'].sum().to_dict()
            }
        }

def main():
    """Função principal para demonstração"""
    print("=== Sistema de Analytics Jurídico - Versão Melhorada ===")
    
    # Cria instância do motor de analytics
    engine = EnhancedAnalyticsEngine()
    
    # Carrega dados
    engine.load_data()
    
    print(f"\nDados carregados: {len(engine.case_data)} casos")
    
    # Gera análise de performance
    print("\n--- Análise de Performance ---")
    performance_report = engine.generate_performance_analysis()
    print(f"Relatório gerado: {performance_report.title}")
    print(f"Insights: {len(performance_report.insights)}")
    print(f"Recomendações: {len(performance_report.recommendations)}")
    print(f"Gráficos: {len(performance_report.charts)}")
    
    # Gera análise preditiva
    print("\n--- Análise Preditiva ---")
    predictive_report = engine.generate_predictive_analysis()
    print(f"Relatório gerado: {predictive_report.title}")
    print(f"Insights: {len(predictive_report.insights)}")
    
    # Gera análise financeira
    print("\n--- Análise Financeira ---")
    financial_report = engine.generate_financial_analysis()
    print(f"Relatório gerado: {financial_report.title}")
    print(f"Receita total: R$ {financial_report.metrics['total_revenue']:,.2f}")
    print(f"Margem de lucro: {financial_report.metrics['profit_margin']:.1f}%")
    
    # Dashboard
    print("\n--- Dashboard ---")
    dashboard_data = engine.get_dashboard_data()
    kpis = dashboard_data['kpis']
    print(f"Total de casos: {kpis['total_cases']}")
    print(f"Casos ativos: {kpis['active_cases']}")
    print(f"Taxa de sucesso: {kpis['success_rate']}%")
    print(f"Receita total: R$ {kpis['total_revenue']:,.2f}")
    
    print(f"\nRelatórios gerados: {len(engine.reports)}")
    
    return engine

if __name__ == "__main__":
    main()

