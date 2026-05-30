#!/usr/bin/env python3
"""
Análise de Resultados e Priorização de Melhorias
Consolida os resultados dos testes e do feedback dos usuários para criar um plano de ação
"""

import json
import pandas as pd
from datetime import datetime

class ResultsAnalyzer:
    """Analisa e consolida os resultados dos testes e feedback"""
    
    def __init__(self, test_results_path, feedback_analysis_path):
        self.test_results = self.load_json(test_results_path)
        self.feedback_analysis = self.load_json(feedback_analysis_path)
    
    def load_json(self, path):
        """Carrega um arquivo JSON"""
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Erro: Arquivo não encontrado em {path}")
            return None
    
    def consolidate_data(self):
        """Consolida os dados de testes e feedback em um único DataFrame"""
        if not self.test_results or not self.feedback_analysis:
            return None
        
        # Dados de testes
        test_scores = self.test_results["overall_stats"]["functionality_scores"]
        
        # Dados de feedback
        feedback_scores = {
            func: data["average_satisfaction"]
            for func, data in self.feedback_analysis["functionality_analysis"].items()
        }
        
        # Consolida em um DataFrame
        df = pd.DataFrame({
            "functionality": list(test_scores.keys()),
            "test_score": list(test_scores.values()),
            "user_satisfaction": [feedback_scores.get(func, 0) for func in test_scores.keys()]
        })
        
        # Adiciona informações de prioridade
        priority_map = {
            item["functionality"]: item["priority_score"]
            for item in self.feedback_analysis["priority_improvements"]
        }
        df["priority_score"] = df["functionality"].map(priority_map)
        
        # Calcula score combinado
        df["combined_score"] = (df["test_score"] * 0.4) + (df["user_satisfaction"] * 0.6)
        
        return df
    
    def generate_improvement_plan(self, consolidated_data):
        """Gera um plano de melhorias priorizado"""
        if consolidated_data is None:
            return None
        
        # Ordena por score combinado e prioridade
        sorted_df = consolidated_data.sort_values(by=["combined_score", "priority_score"], ascending=[True, True])
        
        plan = {
            "plan_timestamp": datetime.now().isoformat(),
            "prioritized_improvements": []
        }
        
        for index, row in sorted_df.iterrows():
            functionality = row["functionality"]
            
            # Busca ações recomendadas
            recommended_actions = []
            for item in self.feedback_analysis["priority_improvements"]:
                if item["functionality"] == functionality:
                    recommended_actions = item["recommended_actions"]
                    break
            
            improvement_item = {
                "functionality": functionality,
                "priority_level": "Alta" if row["combined_score"] < 9.0 else ("Média" if row["combined_score"] < 9.5 else "Baixa"),
                "test_score": row["test_score"],
                "user_satisfaction": row["user_satisfaction"],
                "combined_score": round(row["combined_score"], 2),
                "recommended_actions": recommended_actions
            }
            
            plan["prioritized_improvements"].append(improvement_item)
        
        return plan
    
    def generate_report(self, improvement_plan):
        """Gera um relatório em Markdown com o plano de melhorias"""
        if not improvement_plan:
            return "# Erro ao gerar relatório"
        
        report = f"""# Plano de Melhorias Priorizado - LegalAI Platform

**Data de Geração:** {datetime.now().strftime("%d/%m/%Y %H:%M")}

## 1. Resumo Geral

Este relatório consolida os resultados dos testes automatizados e do feedback dos usuários para criar um plano de ação priorizado para o refinamento das funcionalidades de IA da LegalAI Platform.

## 2. Métricas Consolidadas

| Funcionalidade | Score de Teste | Satisfação do Usuário | Score Combinado |
|---|---|---|---|
"""
        
        df = pd.DataFrame(improvement_plan["prioritized_improvements"])
        for index, row in df.iterrows():
         report += f'| {row["functionality"]} | {row["test_score"]}% | {row["user_satisfaction"]}/10 | {row["combined_score"]}/10 |\n'   
        report += "\n## 3. Plano de Ação Priorizado\n\n"
        for item in improvement_plan["prioritized_improvements"]:
            report += f'### {item["functionality"]} (Prioridade: {item["priority_level"]})\n\n'
            report += f'- **Score Combinado:** {item["combined_score"]}/10\n'
            report += f"- **Ações Recomendadas:**\n"
            for action in item["recommended_actions"]:
                report += f"  - {action}\n"
            report += "\n"
        
        return report

def main():
    """Função principal para análise e priorização"""
    print("Iniciando análise de resultados e priorização de melhorias...")
    
    # Caminhos dos arquivos de resultados
    test_results_path = "/home/ubuntu/ai_testing_environment/results/test_results.json"
    feedback_analysis_path = "/home/ubuntu/ai_testing_environment/results/feedback_analysis.json"
    
    # Cria instância do analisador
    analyzer = ResultsAnalyzer(test_results_path, feedback_analysis_path)
    
    # Consolida dados
    consolidated_data = analyzer.consolidate_data()
    
    if consolidated_data is not None:
        # Gera plano de melhorias
        improvement_plan = analyzer.generate_improvement_plan(consolidated_data)
        
        # Salva plano em JSON
        with open("/home/ubuntu/ai_testing_environment/results/improvement_plan.json", 'w') as f:
            json.dump(improvement_plan, f, indent=2, ensure_ascii=False)
        
        # Gera relatório em Markdown
        report = analyzer.generate_report(improvement_plan)
        with open("/home/ubuntu/ai_testing_environment/reports/improvement_plan_report.md", 'w') as f:
            f.write(report)
        
        print("\nPlano de melhorias gerado com sucesso!")
        print("Relatório salvo em: /home/ubuntu/ai_testing_environment/reports/improvement_plan_report.md")
    else:
        print("\nFalha ao consolidar dados. Verifique os arquivos de resultados.")

if __name__ == "__main__":
    main()





