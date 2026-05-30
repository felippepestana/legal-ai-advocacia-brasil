"""
Funcionalidades Avançadas de Analytics Jurídico
Implementa novas métricas, comparações com benchmarks e visualizações avançadas
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdvancedAnalyticsFeatures:
    """Funcionalidades avançadas de analytics jurídico"""
    
    def __init__(self):
        self.benchmarks = self._load_market_benchmarks()
        self.kpi_definitions = self._load_kpi_definitions()
        
    def _load_market_benchmarks(self) -> Dict[str, Any]:
        """Carrega benchmarks do mercado jurídico"""
        return {
            "success_rates": {
                "civil": 0.65,
                "trabalhista": 0.72,
                "criminal": 0.58,
                "tributario": 0.61,
                "empresarial": 0.69
            },
            "average_case_duration": {
                "civil": 18,  # meses
                "trabalhista": 12,
                "criminal": 24,
                "tributario": 30,
                "empresarial": 15
            },
            "cost_per_case": {
                "civil": 8500.00,
                "trabalhista": 6200.00,
                "criminal": 12000.00,
                "tributario": 15000.00,
                "empresarial": 18000.00
            },
            "client_satisfaction": {
                "overall": 8.2,
                "communication": 8.5,
                "results": 7.9,
                "value_for_money": 7.8
            }
        }
    
    def _load_kpi_definitions(self) -> Dict[str, Dict[str, Any]]:
        """Define KPIs e suas métricas"""
        return {
            "efficiency": {
                "name": "Eficiência Operacional",
                "description": "Mede a eficiência na condução dos casos",
                "formula": "casos_concluidos / tempo_medio_conclusao",
                "target": 2.5,
                "unit": "casos/mês"
            },
            "profitability": {
                "name": "Rentabilidade",
                "description": "Margem de lucro por área de atuação",
                "formula": "(receita - custos) / receita * 100",
                "target": 35.0,
                "unit": "%"
            },
            "client_retention": {
                "name": "Retenção de Clientes",
                "description": "Taxa de clientes que retornam",
                "formula": "clientes_recorrentes / total_clientes * 100",
                "target": 80.0,
                "unit": "%"
            },
            "case_success_rate": {
                "name": "Taxa de Sucesso",
                "description": "Percentual de casos ganhos",
                "formula": "casos_ganhos / total_casos * 100",
                "target": 70.0,
                "unit": "%"
            },
            "billing_efficiency": {
                "name": "Eficiência de Cobrança",
                "description": "Taxa de cobrança efetiva",
                "formula": "valor_recebido / valor_faturado * 100",
                "target": 95.0,
                "unit": "%"
            }
        }
    
    def calculate_advanced_metrics(self, case_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calcula métricas avançadas"""
        df = pd.DataFrame(case_data)
        
        metrics = {}
        
        # Eficiência por advogado
        lawyer_efficiency = df.groupby('lawyer').agg({
            'id': 'count',
            'duration_days': 'mean',
            'value': 'sum'
        }).rename(columns={'id': 'case_count'})
        
        lawyer_efficiency['efficiency_score'] = (
            lawyer_efficiency['case_count'] / 
            (lawyer_efficiency['duration_days'] / 30)
        )
        
        metrics['lawyer_efficiency'] = lawyer_efficiency.to_dict('index')
        
        # Análise de tendências temporais
        df['start_date'] = pd.to_datetime(df['start_date'])
        df['month'] = df['start_date'].dt.to_period('M')
        
        monthly_trends = df.groupby('month').agg({
            'id': 'count',
            'value': 'sum',
            'status': lambda x: (x == 'Ganho').mean()
        }).rename(columns={
            'id': 'case_count',
            'value': 'revenue',
            'status': 'success_rate'
        })
        
        metrics['monthly_trends'] = monthly_trends.to_dict('index')
        
        # Análise de complexidade de casos
        complexity_analysis = df.groupby('area').agg({
            'duration_days': ['mean', 'std'],
            'value': ['mean', 'std'],
            'id': 'count'
        })
        
        complexity_analysis.columns = ['avg_duration', 'std_duration', 'avg_value', 'std_value', 'case_count']
        complexity_analysis['complexity_score'] = (
            complexity_analysis['std_duration'] / complexity_analysis['avg_duration'] +
            complexity_analysis['std_value'] / complexity_analysis['avg_value']
        ) / 2
        
        metrics['complexity_analysis'] = complexity_analysis.to_dict('index')
        
        # ROI por área
        roi_analysis = df.groupby('area').apply(
            lambda x: (x['value'].sum() - x['value'].sum() * 0.3) / (x['value'].sum() * 0.3) * 100
        ).to_dict()
        
        metrics['roi_by_area'] = roi_analysis
        
        return metrics
    
    def compare_with_benchmarks(self, current_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Compara métricas atuais com benchmarks do mercado"""
        comparisons = {}
        
        # Comparação de taxa de sucesso
        if 'success_by_area' in current_metrics:
            success_comparison = {}
            for area, rate in current_metrics['success_by_area'].items():
                benchmark = self.benchmarks['success_rates'].get(area, 0.65)
                difference = rate - benchmark
                performance = "Acima" if difference > 0 else "Abaixo" if difference < 0 else "Igual"
                
                success_comparison[area] = {
                    "current": rate,
                    "benchmark": benchmark,
                    "difference": difference,
                    "performance": performance,
                    "percentage_diff": (difference / benchmark) * 100
                }
            
            comparisons['success_rates'] = success_comparison
        
        # Comparação de duração média
        if 'avg_duration_by_area' in current_metrics:
            duration_comparison = {}
            for area, duration in current_metrics['avg_duration_by_area'].items():
                benchmark = self.benchmarks['average_case_duration'].get(area, 18) * 30  # converter para dias
                difference = duration - benchmark
                performance = "Melhor" if difference < 0 else "Pior" if difference > 0 else "Igual"
                
                duration_comparison[area] = {
                    "current": duration,
                    "benchmark": benchmark,
                    "difference": difference,
                    "performance": performance,
                    "percentage_diff": (difference / benchmark) * 100
                }
            
            comparisons['case_duration'] = duration_comparison
        
        return comparisons
    
    def generate_predictive_insights(self, case_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Gera insights preditivos baseados em dados históricos"""
        df = pd.DataFrame(case_data)
        insights = {}
        
        # Previsão de sucesso baseada em características do caso
        success_factors = df.groupby(['area', 'lawyer']).agg({
            'status': lambda x: (x == 'Ganho').mean(),
            'id': 'count'
        }).rename(columns={'status': 'success_rate', 'id': 'case_count'})
        
        # Filtrar apenas combinações com pelo menos 5 casos
        success_factors = success_factors[success_factors['case_count'] >= 5]
        
        insights['success_predictors'] = success_factors.to_dict('index')
        
        # Análise de sazonalidade
        df['start_date'] = pd.to_datetime(df['start_date'])
        df['month'] = df['start_date'].dt.month
        
        seasonal_analysis = df.groupby('month').agg({
            'id': 'count',
            'value': 'mean'
        }).rename(columns={'id': 'case_count', 'value': 'avg_value'})
        
        insights['seasonal_patterns'] = seasonal_analysis.to_dict('index')
        
        # Previsão de receita para próximos meses
        monthly_revenue = df.groupby(df['start_date'].dt.to_period('M'))['value'].sum()
        
        # Simples previsão baseada na média móvel
        if len(monthly_revenue) >= 3:
            recent_avg = monthly_revenue.tail(3).mean()
            growth_rate = (monthly_revenue.iloc[-1] / monthly_revenue.iloc[-3] - 1) if len(monthly_revenue) >= 3 else 0
            
            predictions = []
            for i in range(1, 4):  # próximos 3 meses
                predicted_value = recent_avg * (1 + growth_rate) ** i
                predictions.append({
                    "month": i,
                    "predicted_revenue": predicted_value,
                    "confidence": max(0.5, 0.9 - i * 0.1)  # confiança diminui com o tempo
                })
            
            insights['revenue_forecast'] = predictions
        
        return insights
    
    def create_advanced_visualizations(self, metrics: Dict[str, Any], output_dir: str = "/home/ubuntu") -> List[str]:
        """Cria visualizações avançadas"""
        chart_files = []
        
        # Configuração de estilo
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
        # 1. Dashboard de KPIs
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle('Dashboard de KPIs Jurídicos', fontsize=16, fontweight='bold')
        
        # KPI 1: Taxa de Sucesso por Área
        if 'success_by_area' in metrics:
            areas = list(metrics['success_by_area'].keys())
            success_rates = [metrics['success_by_area'][area] * 100 for area in areas]
            
            axes[0, 0].bar(areas, success_rates, color='skyblue')
            axes[0, 0].set_title('Taxa de Sucesso por Área (%)')
            axes[0, 0].set_ylabel('Taxa de Sucesso (%)')
            axes[0, 0].tick_params(axis='x', rotation=45)
            
            # Adicionar linha de benchmark
            benchmark_avg = np.mean(list(self.benchmarks['success_rates'].values())) * 100
            axes[0, 0].axhline(y=benchmark_avg, color='red', linestyle='--', label=f'Benchmark: {benchmark_avg:.1f}%')
            axes[0, 0].legend()
        
        # KPI 2: Receita por Mês
        if 'monthly_trends' in metrics:
            months = list(metrics['monthly_trends'].keys())
            revenues = [metrics['monthly_trends'][month]['revenue'] for month in months]
            
            axes[0, 1].plot(range(len(months)), revenues, marker='o', linewidth=2)
            axes[0, 1].set_title('Evolução da Receita Mensal')
            axes[0, 1].set_ylabel('Receita (R$)')
            axes[0, 1].set_xlabel('Mês')
            axes[0, 1].grid(True, alpha=0.3)
        
        # KPI 3: Eficiência por Advogado
        if 'lawyer_efficiency' in metrics:
            lawyers = list(metrics['lawyer_efficiency'].keys())
            efficiency_scores = [metrics['lawyer_efficiency'][lawyer]['efficiency_score'] for lawyer in lawyers]
            
            axes[0, 2].barh(lawyers, efficiency_scores, color='lightgreen')
            axes[0, 2].set_title('Eficiência por Advogado')
            axes[0, 2].set_xlabel('Score de Eficiência')
        
        # KPI 4: Complexidade por Área
        if 'complexity_analysis' in metrics:
            areas = list(metrics['complexity_analysis'].keys())
            complexity_scores = [metrics['complexity_analysis'][area]['complexity_score'] for area in areas]
            
            axes[1, 0].scatter(range(len(areas)), complexity_scores, s=100, alpha=0.7)
            axes[1, 0].set_title('Complexidade por Área')
            axes[1, 0].set_ylabel('Score de Complexidade')
            axes[1, 0].set_xticks(range(len(areas)))
            axes[1, 0].set_xticklabels(areas, rotation=45)
        
        # KPI 5: ROI por Área
        if 'roi_by_area' in metrics:
            areas = list(metrics['roi_by_area'].keys())
            roi_values = list(metrics['roi_by_area'].values())
            
            colors = ['green' if roi > 0 else 'red' for roi in roi_values]
            axes[1, 1].bar(areas, roi_values, color=colors, alpha=0.7)
            axes[1, 1].set_title('ROI por Área (%)')
            axes[1, 1].set_ylabel('ROI (%)')
            axes[1, 1].tick_params(axis='x', rotation=45)
            axes[1, 1].axhline(y=0, color='black', linestyle='-', alpha=0.3)
        
        # KPI 6: Distribuição de Casos
        if 'case_distribution' in metrics:
            statuses = list(metrics['case_distribution'].keys())
            counts = list(metrics['case_distribution'].values())
            
            axes[1, 2].pie(counts, labels=statuses, autopct='%1.1f%%', startangle=90)
            axes[1, 2].set_title('Distribuição de Casos por Status')
        
        plt.tight_layout()
        dashboard_file = f"{output_dir}/advanced_dashboard.png"
        plt.savefig(dashboard_file, dpi=300, bbox_inches='tight')
        plt.close()
        chart_files.append(dashboard_file)
        
        # 2. Análise de Benchmarks
        if 'success_rates' in metrics.get('benchmark_comparison', {}):
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
            fig.suptitle('Comparação com Benchmarks do Mercado', fontsize=14, fontweight='bold')
            
            # Comparação de Taxa de Sucesso
            comparison_data = metrics['benchmark_comparison']['success_rates']
            areas = list(comparison_data.keys())
            current_rates = [comparison_data[area]['current'] * 100 for area in areas]
            benchmark_rates = [comparison_data[area]['benchmark'] * 100 for area in areas]
            
            x = np.arange(len(areas))
            width = 0.35
            
            ax1.bar(x - width/2, current_rates, width, label='Atual', color='skyblue')
            ax1.bar(x + width/2, benchmark_rates, width, label='Benchmark', color='orange')
            ax1.set_title('Taxa de Sucesso: Atual vs Benchmark')
            ax1.set_ylabel('Taxa de Sucesso (%)')
            ax1.set_xticks(x)
            ax1.set_xticklabels(areas, rotation=45)
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # Performance vs Benchmark
            performance_scores = [comparison_data[area]['percentage_diff'] for area in areas]
            colors = ['green' if score > 0 else 'red' for score in performance_scores]
            
            ax2.barh(areas, performance_scores, color=colors, alpha=0.7)
            ax2.set_title('Performance vs Benchmark (%)')
            ax2.set_xlabel('Diferença Percentual (%)')
            ax2.axvline(x=0, color='black', linestyle='-', alpha=0.3)
            
            plt.tight_layout()
            benchmark_file = f"{output_dir}/benchmark_comparison.png"
            plt.savefig(benchmark_file, dpi=300, bbox_inches='tight')
            plt.close()
            chart_files.append(benchmark_file)
        
        return chart_files
    
    def generate_executive_summary(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Gera resumo executivo com insights principais"""
        summary = {
            "period": datetime.now().strftime("%Y-%m"),
            "key_metrics": {},
            "highlights": [],
            "concerns": [],
            "recommendations": []
        }
        
        # Métricas principais
        if 'overall_success_rate' in metrics:
            summary["key_metrics"]["success_rate"] = f"{metrics['overall_success_rate'] * 100:.1f}%"
        
        if 'total_revenue' in metrics:
            summary["key_metrics"]["total_revenue"] = f"R$ {metrics['total_revenue']:,.2f}"
        
        if 'total_cases' in metrics:
            summary["key_metrics"]["total_cases"] = metrics['total_cases']
        
        # Destaques positivos
        if 'benchmark_comparison' in metrics:
            for area, data in metrics['benchmark_comparison'].get('success_rates', {}).items():
                if data['percentage_diff'] > 10:
                    summary["highlights"].append(
                        f"Área {area}: {data['percentage_diff']:.1f}% acima do benchmark de mercado"
                    )
        
        # Preocupações
        if 'roi_by_area' in metrics:
            for area, roi in metrics['roi_by_area'].items():
                if roi < 20:
                    summary["concerns"].append(
                        f"ROI da área {area} está abaixo do esperado ({roi:.1f}%)"
                    )
        
        # Recomendações
        summary["recommendations"] = [
            "Focar em áreas com maior ROI para maximizar rentabilidade",
            "Implementar treinamentos para advogados com menor eficiência",
            "Revisar estratégias em áreas com performance abaixo do benchmark",
            "Considerar automação de processos repetitivos"
        ]
        
        return summary

def main():
    """Função principal para demonstração"""
    print("=== Funcionalidades Avançadas de Analytics ===")
    
    # Dados de exemplo
    sample_data = [
        {
            "id": f"case_{i}",
            "area": np.random.choice(["civil", "trabalhista", "criminal", "tributario", "empresarial"]),
            "lawyer": f"Advogado {np.random.randint(1, 6)}",
            "status": np.random.choice(["Ganho", "Perdido", "Em Andamento"], p=[0.6, 0.2, 0.2]),
            "start_date": (datetime.now() - timedelta(days=np.random.randint(30, 730))).strftime("%Y-%m-%d"),
            "duration_days": np.random.randint(30, 600),
            "value": np.random.uniform(5000, 50000)
        }
        for i in range(200)
    ]
    
    # Cria instância das funcionalidades avançadas
    advanced_analytics = AdvancedAnalyticsFeatures()
    
    # Calcula métricas avançadas
    print("\nCalculando métricas avançadas...")
    advanced_metrics = advanced_analytics.calculate_advanced_metrics(sample_data)
    
    # Compara com benchmarks
    print("Comparando com benchmarks do mercado...")
    benchmark_comparison = advanced_analytics.compare_with_benchmarks({
        'success_by_area': {area: np.random.uniform(0.5, 0.8) for area in ["civil", "trabalhista", "criminal"]},
        'avg_duration_by_area': {area: np.random.uniform(300, 600) for area in ["civil", "trabalhista", "criminal"]}
    })
    
    advanced_metrics['benchmark_comparison'] = benchmark_comparison
    
    # Gera insights preditivos
    print("Gerando insights preditivos...")
    predictive_insights = advanced_analytics.generate_predictive_insights(sample_data)
    advanced_metrics.update(predictive_insights)
    
    # Cria visualizações
    print("Criando visualizações avançadas...")
    chart_files = advanced_analytics.create_advanced_visualizations(advanced_metrics)
    print(f"Gráficos salvos: {chart_files}")
    
    # Gera resumo executivo
    print("Gerando resumo executivo...")
    executive_summary = advanced_analytics.generate_executive_summary(advanced_metrics)
    
    print("\n=== Resumo Executivo ===")
    print(f"Período: {executive_summary['period']}")
    print(f"Métricas principais: {executive_summary['key_metrics']}")
    print(f"Destaques: {len(executive_summary['highlights'])}")
    print(f"Preocupações: {len(executive_summary['concerns'])}")
    print(f"Recomendações: {len(executive_summary['recommendations'])}")
    
    return advanced_analytics

if __name__ == "__main__":
    main()

