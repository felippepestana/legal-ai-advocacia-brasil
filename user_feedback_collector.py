#!/usr/bin/env python3
"""
Sistema de Coleta de Feedback de Usuários
Simula coleta de feedback real de advogados e usuários da plataforma
"""

import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any
import uuid

class UserFeedbackCollector:
    """Coleta e processa feedback de usuários sobre as funcionalidades de IA"""
    
    def __init__(self):
        self.feedback_data = []
        self.user_profiles = self.generate_user_profiles()
    
    def generate_user_profiles(self) -> List[Dict]:
        """Gera perfis de usuários simulados"""
        profiles = [
            {
                "user_id": str(uuid.uuid4()),
                "name": "Dr. Carlos Santos",
                "role": "Advogado Sênior",
                "experience_years": 15,
                "specialization": "Direito Civil",
                "firm_size": "Grande",
                "tech_comfort": "Alto"
            },
            {
                "user_id": str(uuid.uuid4()),
                "name": "Dra. Paula Lima",
                "role": "Advogada Trabalhista",
                "experience_years": 8,
                "specialization": "Direito Trabalhista",
                "firm_size": "Médio",
                "tech_comfort": "Médio"
            },
            {
                "user_id": str(uuid.uuid4()),
                "name": "Dr. João Silva",
                "role": "Advogado Autônomo",
                "experience_years": 5,
                "specialization": "Direito do Consumidor",
                "firm_size": "Pequeno",
                "tech_comfort": "Alto"
            },
            {
                "user_id": str(uuid.uuid4()),
                "name": "Dra. Ana Costa",
                "role": "Coordenadora Jurídica",
                "experience_years": 12,
                "specialization": "Direito Empresarial",
                "firm_size": "Grande",
                "tech_comfort": "Médio"
            },
            {
                "user_id": str(uuid.uuid4()),
                "name": "Dr. Roberto Oliveira",
                "role": "Advogado Júnior",
                "experience_years": 2,
                "specialization": "Direito Penal",
                "firm_size": "Médio",
                "tech_comfort": "Alto"
            }
        ]
        return profiles
    
    def simulate_usage_session(self, user_profile: Dict, functionality: str) -> Dict:
        """Simula uma sessão de uso de uma funcionalidade"""
        
        # Define padrões de feedback baseados no perfil do usuário
        tech_comfort_multiplier = {
            "Alto": 1.2,
            "Médio": 1.0,
            "Baixo": 0.8
        }.get(user_profile["tech_comfort"], 1.0)
        
        experience_multiplier = min(1.0 + (user_profile["experience_years"] / 20), 1.5)
        
        # Simula métricas de uso
        base_satisfaction = random.uniform(7.5, 9.5)
        satisfaction = min(10, base_satisfaction * tech_comfort_multiplier * experience_multiplier)
        
        session_data = {
            "session_id": str(uuid.uuid4()),
            "user_id": user_profile["user_id"],
            "functionality": functionality,
            "timestamp": datetime.now().isoformat(),
            "duration_minutes": random.uniform(5, 45),
            "tasks_completed": random.randint(1, 8),
            "satisfaction_score": round(satisfaction, 1),
            "ease_of_use": round(random.uniform(7.0, 9.5), 1),
            "accuracy_perception": round(random.uniform(8.0, 9.8), 1),
            "speed_perception": round(random.uniform(7.5, 9.2), 1),
            "would_recommend": satisfaction >= 8.0,
            "issues_encountered": random.choice([True, False]) if satisfaction < 8.5 else False
        }
        
        return session_data
    
    def generate_qualitative_feedback(self, user_profile: Dict, functionality: str, session_data: Dict) -> List[str]:
        """Gera feedback qualitativo baseado no perfil e sessão"""
        
        feedback_templates = {
            "Análise Inteligente de Documentos": [
                "A extração de entidades está muito precisa, economizou muito tempo na análise inicial",
                "Gostaria que identificasse mais conceitos específicos da minha área de atuação",
                "As recomendações da IA são úteis, mas às vezes muito genéricas",
                "Excelente para documentos simples, mas tem dificuldade com contratos complexos",
                "A interface é intuitiva, consegui usar sem treinamento"
            ],
            "Automação de Workflows": [
                "Os workflows personalizáveis são um diferencial, adaptei perfeitamente ao meu escritório",
                "Precisa de mais templates prontos para diferentes tipos de processo",
                "A automação de tarefas repetitivas aumentou muito minha produtividade",
                "Gostaria de mais integração com outros sistemas que já uso",
                "O sistema de notificações funciona bem, não perco mais prazos"
            ],
            "Assistente Virtual Jurídico": [
                "O assistente entende bem as perguntas jurídicas, muito melhor que chatbots genéricos",
                "Às vezes as respostas são muito longas, preferia respostas mais diretas",
                "Excelente para esclarecer dúvidas rápidas durante a redação de peças",
                "Precisa melhorar o conhecimento sobre jurisprudência mais recente",
                "A interface de chat é familiar e fácil de usar"
            ],
            "Gestão Inteligente de Prazos": [
                "Nunca mais perdi um prazo desde que comecei a usar, é fundamental",
                "Os alertas chegam no momento certo, nem muito cedo nem muito tarde",
                "Gostaria de integração com meu calendário pessoal",
                "A detecção automática de prazos em publicações é impressionante",
                "Precisa melhorar a categorização dos tipos de prazo"
            ],
            "Analytics Jurídico": [
                "Os insights sobre performance me ajudam a tomar decisões estratégicas",
                "Os gráficos são claros e informativos",
                "Gostaria de mais comparações com dados do mercado",
                "Excelente para apresentações para clientes e sócios",
                "Precisa de mais filtros para análises específicas"
            ],
            "Geração de Documentos": [
                "Os documentos gerados têm qualidade profissional",
                "Economiza muito tempo na elaboração de peças padrão",
                "Precisa de mais templates para minha área específica",
                "A personalização é boa, mas poderia ser mais flexível",
                "Excelente para documentos simples, mas precisa de revisão em casos complexos"
            ],
            "Pesquisa Inteligente": [
                "Encontra jurisprudência relevante muito mais rápido que pesquisa manual",
                "Os resultados são bem organizados por relevância",
                "Gostaria de mais filtros por tribunal e data",
                "A busca por linguagem natural funciona muito bem",
                "Precisa incluir mais fontes de doutrina"
            ],
            "Cálculos Jurídicos Avançados": [
                "Os cálculos são precisos e confiáveis",
                "Interface muito mais amigável que planilhas complexas",
                "Gostaria de mais tipos de cálculo trabalhista",
                "Excelente para validar cálculos feitos manualmente",
                "Precisa de mais explicações sobre as fórmulas utilizadas"
            ]
        }
        
        # Seleciona feedback baseado na satisfação
        available_feedback = feedback_templates.get(functionality, ["Funcionalidade interessante"])
        
        if session_data["satisfaction_score"] >= 9.0:
            # Usuário muito satisfeito - feedback mais positivo
            selected_feedback = random.sample(available_feedback[:3], min(2, len(available_feedback[:3])))
        elif session_data["satisfaction_score"] >= 7.5:
            # Usuário satisfeito - mix de positivo e sugestões
            selected_feedback = random.sample(available_feedback, min(2, len(available_feedback)))
        else:
            # Usuário menos satisfeito - mais críticas construtivas
            selected_feedback = random.sample(available_feedback[2:], min(2, len(available_feedback[2:])))
        
        return selected_feedback
    
    def collect_feedback_for_functionality(self, functionality: str, num_sessions: int = 5) -> List[Dict]:
        """Coleta feedback para uma funcionalidade específica"""
        
        functionality_feedback = []
        
        for _ in range(num_sessions):
            # Seleciona usuário aleatório
            user = random.choice(self.user_profiles)
            
            # Simula sessão de uso
            session = self.simulate_usage_session(user, functionality)
            
            # Gera feedback qualitativo
            qualitative_feedback = self.generate_qualitative_feedback(user, functionality, session)
            
            # Combina dados
            feedback_entry = {
                **session,
                "user_profile": user,
                "qualitative_feedback": qualitative_feedback,
                "improvement_suggestions": self.generate_improvement_suggestions(functionality, session)
            }
            
            functionality_feedback.append(feedback_entry)
        
        return functionality_feedback
    
    def generate_improvement_suggestions(self, functionality: str, session_data: Dict) -> List[str]:
        """Gera sugestões de melhoria baseadas na sessão"""
        
        suggestions = []
        
        if session_data["satisfaction_score"] < 8.0:
            suggestions.append("Melhorar usabilidade da interface")
        
        if session_data["speed_perception"] < 8.0:
            suggestions.append("Otimizar performance e velocidade de resposta")
        
        if session_data["accuracy_perception"] < 9.0:
            suggestions.append("Refinar algoritmos para maior precisão")
        
        if session_data["issues_encountered"]:
            suggestions.append("Corrigir bugs e problemas de estabilidade")
        
        # Sugestões específicas por funcionalidade
        specific_suggestions = {
            "Análise Inteligente de Documentos": [
                "Expandir base de conhecimento jurídico",
                "Melhorar reconhecimento de documentos complexos"
            ],
            "Automação de Workflows": [
                "Adicionar mais templates pré-configurados",
                "Melhorar integração com sistemas externos"
            ],
            "Assistente Virtual Jurídico": [
                "Atualizar base de conhecimento jurisprudencial",
                "Implementar respostas mais concisas"
            ],
            "Gestão Inteligente de Prazos": [
                "Adicionar integração com calendários externos",
                "Melhorar categorização de tipos de prazo"
            ],
            "Analytics Jurídico": [
                "Adicionar mais métricas e KPIs",
                "Implementar comparações com benchmarks do mercado"
            ],
            "Geração de Documentos": [
                "Expandir biblioteca de templates",
                "Melhorar personalização de documentos"
            ],
            "Pesquisa Inteligente": [
                "Adicionar mais fontes de dados",
                "Implementar filtros avançados"
            ],
            "Cálculos Jurídicos Avançados": [
                "Adicionar mais tipos de cálculo",
                "Implementar explicações detalhadas das fórmulas"
            ]
        }
        
        if functionality in specific_suggestions:
            suggestions.extend(random.sample(specific_suggestions[functionality], 1))
        
        return suggestions
    
    def collect_all_feedback(self) -> Dict:
        """Coleta feedback para todas as funcionalidades"""
        
        functionalities = [
            "Análise Inteligente de Documentos",
            "Automação de Workflows",
            "Assistente Virtual Jurídico",
            "Gestão Inteligente de Prazos",
            "Analytics Jurídico",
            "Geração de Documentos",
            "Pesquisa Inteligente",
            "Cálculos Jurídicos Avançados"
        ]
        
        all_feedback = {
            "collection_timestamp": datetime.now().isoformat(),
            "total_users": len(self.user_profiles),
            "functionalities": {}
        }
        
        for functionality in functionalities:
            print(f"Coletando feedback para: {functionality}")
            feedback = self.collect_feedback_for_functionality(functionality, num_sessions=8)
            all_feedback["functionalities"][functionality] = feedback
        
        return all_feedback
    
    def analyze_feedback(self, feedback_data: Dict) -> Dict:
        """Analisa o feedback coletado e gera insights"""
        
        analysis = {
            "analysis_timestamp": datetime.now().isoformat(),
            "overall_metrics": {},
            "functionality_analysis": {},
            "priority_improvements": [],
            "user_satisfaction_trends": {}
        }
        
        # Análise geral
        all_sessions = []
        for functionality, sessions in feedback_data["functionalities"].items():
            all_sessions.extend(sessions)
        
        if all_sessions:
            avg_satisfaction = sum(s["satisfaction_score"] for s in all_sessions) / len(all_sessions)
            avg_ease_of_use = sum(s["ease_of_use"] for s in all_sessions) / len(all_sessions)
            avg_accuracy = sum(s["accuracy_perception"] for s in all_sessions) / len(all_sessions)
            avg_speed = sum(s["speed_perception"] for s in all_sessions) / len(all_sessions)
            recommendation_rate = sum(1 for s in all_sessions if s["would_recommend"]) / len(all_sessions) * 100
            
            analysis["overall_metrics"] = {
                "average_satisfaction": round(avg_satisfaction, 2),
                "average_ease_of_use": round(avg_ease_of_use, 2),
                "average_accuracy_perception": round(avg_accuracy, 2),
                "average_speed_perception": round(avg_speed, 2),
                "recommendation_rate": round(recommendation_rate, 1),
                "total_sessions": len(all_sessions)
            }
        
        # Análise por funcionalidade
        for functionality, sessions in feedback_data["functionalities"].items():
            if sessions:
                func_avg_satisfaction = sum(s["satisfaction_score"] for s in sessions) / len(sessions)
                func_issues = sum(1 for s in sessions if s["issues_encountered"])
                
                # Coleta sugestões mais comuns
                all_suggestions = []
                for session in sessions:
                    all_suggestions.extend(session["improvement_suggestions"])
                
                suggestion_counts = {}
                for suggestion in all_suggestions:
                    suggestion_counts[suggestion] = suggestion_counts.get(suggestion, 0) + 1
                
                top_suggestions = sorted(suggestion_counts.items(), key=lambda x: x[1], reverse=True)[:3]
                
                analysis["functionality_analysis"][functionality] = {
                    "average_satisfaction": round(func_avg_satisfaction, 2),
                    "issues_reported": func_issues,
                    "total_sessions": len(sessions),
                    "top_improvement_suggestions": [s[0] for s in top_suggestions]
                }
        
        # Priorização de melhorias
        functionality_scores = []
        for func, data in analysis["functionality_analysis"].items():
            score = data["average_satisfaction"] - (data["issues_reported"] * 0.5)
            functionality_scores.append((func, score, data["issues_reported"]))
        
        # Ordena por menor satisfação e mais problemas
        functionality_scores.sort(key=lambda x: (x[1], -x[2]))
        
        analysis["priority_improvements"] = [
            {
                "functionality": func,
                "priority_score": round(score, 2),
                "issues_count": issues,
                "recommended_actions": analysis["functionality_analysis"][func]["top_improvement_suggestions"]
            }
            for func, score, issues in functionality_scores[:5]
        ]
        
        return analysis

def main():
    """Função principal para coleta e análise de feedback"""
    print("Iniciando coleta de feedback de usuários...")
    
    collector = UserFeedbackCollector()
    
    # Coleta feedback
    feedback_data = collector.collect_all_feedback()
    
    # Salva dados brutos
    with open('/home/ubuntu/ai_testing_environment/results/user_feedback.json', 'w') as f:
        json.dump(feedback_data, f, indent=2, ensure_ascii=False)
    
    # Analisa feedback
    print("\nAnalisando feedback coletado...")
    analysis = collector.analyze_feedback(feedback_data)
    
    # Salva análise
    with open('/home/ubuntu/ai_testing_environment/results/feedback_analysis.json', 'w') as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)
    
    # Exibe resultados
    print(f"\nResultados da Coleta de Feedback:")
    print(f"Total de sessões: {analysis['overall_metrics']['total_sessions']}")
    print(f"Satisfação média: {analysis['overall_metrics']['average_satisfaction']}/10")
    print(f"Taxa de recomendação: {analysis['overall_metrics']['recommendation_rate']}%")
    
    print(f"\nTop 3 funcionalidades para melhoria:")
    for i, improvement in enumerate(analysis['priority_improvements'][:3], 1):
        print(f"{i}. {improvement['functionality']} (Score: {improvement['priority_score']})")
    
    return analysis

if __name__ == "__main__":
    main()

