#!/usr/bin/env python3
"""
Assistente Virtual Jurídico - Versão Melhorada
Implementa melhorias: respostas mais concisas, base de conhecimento atualizada
e algoritmos refinados para maior precisão
"""

import json
import re
import os
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
import openai
import time

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QueryType(Enum):
    """Tipos de consultas jurídicas"""
    PROCEDURAL = "Processual"
    SUBSTANTIVE = "Material"
    CALCULATION = "Cálculo"
    JURISPRUDENCE = "Jurisprudência"
    LEGISLATION = "Legislação"
    PRACTICAL = "Prática"
    DEADLINE = "Prazo"
    DOCUMENT = "Documento"

class ResponseStyle(Enum):
    """Estilos de resposta"""
    CONCISE = "Conciso"
    DETAILED = "Detalhado"
    PRACTICAL = "Prático"
    ACADEMIC = "Acadêmico"

@dataclass
class LegalQuery:
    """Consulta jurídica"""
    id: str
    text: str
    type: QueryType
    context: Dict[str, Any]
    user_id: str
    timestamp: datetime

@dataclass
class LegalResponse:
    """Resposta jurídica"""
    query_id: str
    answer: str
    confidence: float
    sources: List[str]
    related_concepts: List[str]
    follow_up_questions: List[str]
    response_time: float
    style: ResponseStyle

class EnhancedKnowledgeBase:
    """Base de conhecimento jurídica aprimorada"""
    
    def __init__(self):
        self.legal_concepts = self._load_legal_concepts()
        self.jurisprudence = self._load_jurisprudence()
        self.legislation = self._load_legislation()
        self.practical_guides = self._load_practical_guides()
        self.calculation_formulas = self._load_calculation_formulas()
    
    def _load_legal_concepts(self) -> Dict[str, Dict[str, Any]]:
        """Carrega conceitos jurídicos fundamentais"""
        return {
            "danos_morais": {
                "definition": "Lesão a direitos da personalidade, causando dor, sofrimento, humilhação ou abalo à reputação",
                "legal_basis": ["Art. 186 CC", "Art. 927 CC", "Art. 5º, V e X CF"],
                "calculation_criteria": ["Gravidade da ofensa", "Condição econômica das partes", "Caráter pedagógico"],
                "recent_values": "R$ 5.000 a R$ 50.000 (casos típicos)",
                "keywords": ["honra", "imagem", "dignidade", "sofrimento", "humilhação"]
            },
            "danos_materiais": {
                "definition": "Prejuízo econômico efetivo e comprovado ao patrimônio",
                "legal_basis": ["Art. 402 CC", "Art. 403 CC"],
                "components": ["Dano emergente", "Lucros cessantes"],
                "proof_requirements": "Comprovação do nexo causal e extensão do dano",
                "keywords": ["prejuízo", "patrimônio", "lucro", "emergente", "cessante"]
            },
            "responsabilidade_civil": {
                "definition": "Obrigação de reparar dano causado a outrem",
                "elements": ["Conduta", "Dano", "Nexo causal", "Culpa (subjetiva)"],
                "types": ["Subjetiva", "Objetiva"],
                "legal_basis": ["Art. 186 CC", "Art. 927 CC"],
                "keywords": ["reparação", "culpa", "dolo", "nexo", "causal"]
            },
            "cdc_consumidor": {
                "definition": "Relação jurídica entre fornecedor e consumidor final",
                "principles": ["Vulnerabilidade", "Hipossuficiência", "Boa-fé"],
                "rights": ["Informação", "Segurança", "Reparação", "Inversão do ônus"],
                "legal_basis": ["Lei 8.078/90"],
                "keywords": ["consumidor", "fornecedor", "produto", "serviço", "defeito"]
            },
            "trabalhista_rescisao": {
                "definition": "Término do contrato de trabalho e verbas devidas",
                "types": ["Sem justa causa", "Com justa causa", "Pedido de demissão", "Acordo"],
                "verbas": ["Saldo salário", "Aviso prévio", "13º", "Férias", "FGTS"],
                "deadlines": ["10 dias úteis (até 10 empregados)", "1º dia útil (mais de 10)"],
                "keywords": ["rescisão", "verbas", "aviso", "prévio", "fgts"]
            }
        }
    
    def _load_jurisprudence(self) -> Dict[str, List[Dict[str, Any]]]:
        """Carrega jurisprudência relevante"""
        return {
            "danos_morais": [
                {
                    "court": "STJ",
                    "case": "REsp 1.737.428/RJ",
                    "summary": "Inscrição indevida em órgãos de proteção ao crédito gera dano moral presumido",
                    "value_range": "R$ 5.000 a R$ 15.000",
                    "year": 2023
                },
                {
                    "court": "TJSP",
                    "case": "Apelação 1234567-89.2023.8.26.0100",
                    "summary": "Dano moral por negativação indevida - valor proporcional",
                    "value_range": "R$ 8.000",
                    "year": 2024
                }
            ],
            "trabalhista": [
                {
                    "court": "TST",
                    "case": "RR 123456-78.2023.5.02.0001",
                    "summary": "Horas extras habituais integram base de cálculo do 13º salário",
                    "impact": "Cálculo de verbas rescisórias",
                    "year": 2024
                }
            ]
        }
    
    def _load_legislation(self) -> Dict[str, Dict[str, Any]]:
        """Carrega legislação atualizada"""
        return {
            "codigo_civil": {
                "articles": {
                    "186": "Aquele que, por ação ou omissão voluntária, negligência ou imprudência, violar direito e causar dano a outrem, ainda que exclusivamente moral, comete ato ilícito.",
                    "927": "Aquele que, por ato ilícito (arts. 186 e 187), causar dano a outrem, fica obrigado a repará-lo.",
                    "402": "As perdas e danos devidas ao credor abrangem, além do que ele efetivamente perdeu, o que razoavelmente deixou de lucrar.",
                    "944": "A indenização mede-se pela extensão do dano."
                }
            },
            "cdc": {
                "articles": {
                    "6": "São direitos básicos do consumidor: I - a proteção da vida, saúde e segurança...",
                    "14": "O fornecedor de serviços responde, independentemente da existência de culpa...",
                    "17": "Para os efeitos desta Seção, equiparam-se aos consumidores todas as vítimas do evento."
                }
            },
            "clt": {
                "articles": {
                    "477": "É assegurado a todo empregado, não existindo prazo estipulado para a terminação do respectivo contrato...",
                    "7": "São direitos dos trabalhadores urbanos e rurais..."
                }
            }
        }
    
    def _load_practical_guides(self) -> Dict[str, Dict[str, Any]]:
        """Carrega guias práticos"""
        return {
            "peticao_inicial": {
                "structure": ["Endereçamento", "Qualificação", "Fatos", "Direito", "Pedidos", "Valor da causa"],
                "requirements": ["CPC Art. 319", "Documentos essenciais", "Procuração"],
                "tips": ["Narrativa clara", "Fundamentação legal", "Pedidos específicos"]
            },
            "contestacao": {
                "deadline": "15 dias (CPC Art. 335)",
                "structure": ["Preliminares", "Mérito", "Pedidos"],
                "defenses": ["Ilegitimidade", "Prescrição", "Decadência", "Falta de interesse"]
            },
            "calculo_trabalhista": {
                "verbas": {
                    "aviso_previo": "30 dias + 3 dias por ano trabalhado",
                    "ferias": "1/3 constitucional + valor proporcional",
                    "decimo_terceiro": "Valor proporcional aos meses trabalhados"
                }
            }
        }
    
    def _load_calculation_formulas(self) -> Dict[str, Dict[str, Any]]:
        """Carrega fórmulas de cálculo"""
        return {
            "juros_simples": {
                "formula": "J = C * i * t",
                "variables": {"C": "Capital", "i": "Taxa", "t": "Tempo"},
                "application": "Cálculos trabalhistas básicos"
            },
            "juros_compostos": {
                "formula": "M = C * (1 + i)^t",
                "variables": {"M": "Montante", "C": "Capital", "i": "Taxa", "t": "Tempo"},
                "application": "Correção monetária"
            },
            "inss": {
                "formula": "Progressiva por faixas",
                "rates": {"Até R$ 1.320": "7.5%", "R$ 1.320,01 a R$ 2.571,29": "9%"},
                "application": "Cálculo de contribuição previdenciária"
            }
        }
    
    def search_knowledge(self, query: str, query_type: QueryType) -> Dict[str, Any]:
        """Busca conhecimento relevante para a consulta"""
        query_lower = query.lower()
        relevant_content = {
            "concepts": [],
            "jurisprudence": [],
            "legislation": [],
            "practical_guides": [],
            "formulas": []
        }
        
        # Busca conceitos
        for concept_id, concept_data in self.legal_concepts.items():
            if any(keyword in query_lower for keyword in concept_data.get("keywords", [])):
                relevant_content["concepts"].append({
                    "id": concept_id,
                    "data": concept_data
                })
        
        # Busca jurisprudência
        for area, cases in self.jurisprudence.items():
            if area in query_lower or any(keyword in query_lower for keyword in area.split("_")):
                relevant_content["jurisprudence"].extend(cases)
        
        # Busca legislação
        for law, articles in self.legislation.items():
            if law in query_lower:
                relevant_content["legislation"].append({
                    "law": law,
                    "articles": articles["articles"]
                })
        
        # Busca guias práticos
        for guide_id, guide_data in self.practical_guides.items():
            if guide_id in query_lower or any(word in query_lower for word in guide_id.split("_")):
                relevant_content["practical_guides"].append({
                    "id": guide_id,
                    "data": guide_data
                })
        
        # Busca fórmulas
        if query_type == QueryType.CALCULATION:
            for formula_id, formula_data in self.calculation_formulas.items():
                if any(word in query_lower for word in formula_id.split("_")):
                    relevant_content["formulas"].append({
                        "id": formula_id,
                        "data": formula_data
                    })
        
        return relevant_content

class QueryClassifier:
    """Classificador de consultas jurídicas"""
    
    def __init__(self):
        self.patterns = {
            QueryType.PROCEDURAL: [
                r"como\s+protocolar", r"prazo\s+para", r"como\s+fazer",
                r"procedimento", r"etapas", r"passo\s+a\s+passo"
            ],
            QueryType.CALCULATION: [
                r"calcul", r"quanto", r"valor", r"juros", r"correção",
                r"multa", r"honorários", r"verbas"
            ],
            QueryType.JURISPRUDENCE: [
                r"jurisprudência", r"precedente", r"tribunal", r"stj", r"stf",
                r"decisão", r"entendimento"
            ],
            QueryType.LEGISLATION: [
                r"artigo", r"lei", r"código", r"constituição", r"cdc",
                r"clt", r"cpc", r"legislação"
            ],
            QueryType.DEADLINE: [
                r"prazo", r"quando", r"até\s+quando", r"vencimento",
                r"prescrição", r"decadência"
            ],
            QueryType.DOCUMENT: [
                r"modelo", r"template", r"petição", r"contestação",
                r"recurso", r"documento", r"formulário"
            ]
        }
    
    def classify_query(self, query: str) -> Tuple[QueryType, float]:
        """Classifica o tipo da consulta"""
        query_lower = query.lower()
        scores = {}
        
        for query_type, patterns in self.patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, query_lower))
                score += matches
            
            if score > 0:
                scores[query_type] = score / len(patterns)
        
        if not scores:
            return QueryType.SUBSTANTIVE, 0.5
        
        best_type = max(scores, key=scores.get)
        confidence = min(scores[best_type], 1.0)
        
        return best_type, confidence

class ResponseGenerator:
    """Gerador de respostas aprimorado"""
    
    def __init__(self, knowledge_base: EnhancedKnowledgeBase):
        self.knowledge_base = knowledge_base
        self._client: Optional[openai.OpenAI] = None
    
    def _get_client(self) -> Optional[openai.OpenAI]:
        if self._client is not None:
            return self._client
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            return None
        try:
            self._client = openai.OpenAI(api_key=api_key)
        except Exception as exc:
            logger.warning("OpenAI indisponível: %s", exc)
            return None
        return self._client
    
    def generate_response(self, query: LegalQuery, style: ResponseStyle = ResponseStyle.CONCISE) -> LegalResponse:
        """Gera resposta para consulta jurídica"""
        start_time = time.time()
        
        # Busca conhecimento relevante
        relevant_knowledge = self.knowledge_base.search_knowledge(query.text, query.type)
        
        # Constrói contexto para IA
        context = self._build_context(query, relevant_knowledge, style)
        
        # Gera resposta usando IA
        ai_response = self._generate_ai_response(context, style, relevant_knowledge)
        
        # Extrai informações da resposta
        answer = ai_response.get("answer", "")
        sources = self._extract_sources(relevant_knowledge)
        related_concepts = self._extract_related_concepts(relevant_knowledge)
        follow_up_questions = ai_response.get("follow_up_questions", [])
        
        response_time = time.time() - start_time
        
        return LegalResponse(
            query_id=query.id,
            answer=answer,
            confidence=ai_response.get("confidence", 0.8),
            sources=sources,
            related_concepts=related_concepts,
            follow_up_questions=follow_up_questions,
            response_time=response_time,
            style=style
        )
    
    def _build_context(self, query: LegalQuery, knowledge: Dict[str, Any], style: ResponseStyle) -> str:
        """Constrói contexto para a IA"""
        context_parts = [
            f"Consulta jurídica: {query.text}",
            f"Tipo: {query.type.value}",
            f"Estilo de resposta: {style.value}"
        ]
        
        # Adiciona conceitos relevantes
        if knowledge["concepts"]:
            context_parts.append("Conceitos relevantes:")
            for concept in knowledge["concepts"][:3]:
                context_parts.append(f"- {concept['data']['definition']}")
        
        # Adiciona jurisprudência
        if knowledge["jurisprudence"]:
            context_parts.append("Jurisprudência relevante:")
            for case in knowledge["jurisprudence"][:2]:
                context_parts.append(f"- {case['court']}: {case['summary']}")
        
        # Adiciona legislação
        if knowledge["legislation"]:
            context_parts.append("Base legal:")
            for law_info in knowledge["legislation"][:2]:
                for article, text in list(law_info["articles"].items())[:2]:
                    context_parts.append(f"- Art. {article}: {text[:100]}...")
        
        return "\n".join(context_parts)
    
    def _fallback_response(
        self, knowledge: Dict[str, Any], style: ResponseStyle
    ) -> Dict[str, Any]:
        """Resposta local quando OpenAI não está configurado."""
        parts: List[str] = []
        for concept in knowledge.get("concepts", [])[:2]:
            data = concept.get("data", {})
            definition = data.get("definition")
            if definition:
                parts.append(definition)
            basis = data.get("legal_basis")
            if basis:
                parts.append(f"Base legal: {', '.join(basis)}.")
            if style == ResponseStyle.PRACTICAL and data.get("calculation_criteria"):
                parts.append(
                    "Critérios práticos: "
                    + ", ".join(data["calculation_criteria"])
                    + "."
                )
        for case in knowledge.get("jurisprudence", [])[:1]:
            parts.append(f"{case.get('court', 'Tribunal')}: {case.get('summary', '')}")
        if not parts:
            parts.append(
                "Consulta registrada. Para resposta aprofundada, configure GEMINI_API_KEY "
                "ou OPENAI_API_KEY, ou refine a pergunta com área do direito e contexto."
            )
        return {
            "answer": "\n\n".join(parts),
            "confidence": 0.65 if parts else 0.3,
            "follow_up_questions": [],
        }

    def _generate_ai_response(
        self,
        context: str,
        style: ResponseStyle,
        knowledge: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Gera resposta usando IA"""
        client = self._get_client()
        if client is None:
            return self._fallback_response(knowledge or {}, style)

        style_instructions = {
            ResponseStyle.CONCISE: "Responda de forma concisa e direta, máximo 3 parágrafos.",
            ResponseStyle.DETAILED: "Forneça uma resposta detalhada e completa.",
            ResponseStyle.PRACTICAL: "Foque em aspectos práticos e aplicáveis.",
            ResponseStyle.ACADEMIC: "Use linguagem técnica e acadêmica."
        }
        
        system_prompt = f"""
        Você é um assistente jurídico especializado em direito brasileiro.
        {style_instructions[style]}
        
        Estruture sua resposta em:
        1. Resposta direta à pergunta
        2. Base legal (se aplicável)
        3. Considerações práticas (se relevante)
        
        Seja preciso, cite fontes quando possível e mantenha linguagem profissional.
        """
        
        try:
            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": context}
                ],
                max_tokens=800 if style == ResponseStyle.CONCISE else 1500,
                temperature=0.3
            )
            
            answer = response.choices[0].message.content
            
            # Gera perguntas de acompanhamento
            follow_up_response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": "Gere 2-3 perguntas de acompanhamento relacionadas à consulta jurídica. Retorne apenas as perguntas, uma por linha."},
                    {"role": "user", "content": f"Consulta: {context}\nResposta: {answer}"}
                ],
                max_tokens=200,
                temperature=0.5
            )
            
            follow_up_questions = [
                q.strip() for q in follow_up_response.choices[0].message.content.split('\n') 
                if q.strip() and q.strip().endswith('?')
            ]
            
            return {
                "answer": answer,
                "confidence": 0.85,
                "follow_up_questions": follow_up_questions[:3]
            }
            
        except Exception as e:
            logger.error(f"Erro na geração de resposta: {e}")
            return {
                "answer": "Desculpe, não foi possível gerar uma resposta no momento. Tente novamente.",
                "confidence": 0.1,
                "follow_up_questions": []
            }
    
    def _extract_sources(self, knowledge: Dict[str, Any]) -> List[str]:
        """Extrai fontes do conhecimento relevante"""
        sources = []
        
        # Adiciona conceitos como fontes
        for concept in knowledge["concepts"]:
            if "legal_basis" in concept["data"]:
                sources.extend(concept["data"]["legal_basis"])
        
        # Adiciona jurisprudência
        for case in knowledge["jurisprudence"]:
            sources.append(f"{case['court']} - {case.get('case', 'Caso não identificado')}")
        
        # Adiciona legislação
        for law_info in knowledge["legislation"]:
            law_name = law_info["law"].replace("_", " ").title()
            sources.append(law_name)
        
        return list(set(sources))  # Remove duplicatas
    
    def _extract_related_concepts(self, knowledge: Dict[str, Any]) -> List[str]:
        """Extrai conceitos relacionados"""
        concepts = []
        
        for concept in knowledge["concepts"]:
            concept_name = concept["id"].replace("_", " ").title()
            concepts.append(concept_name)
        
        return concepts

class EnhancedVirtualAssistant:
    """Assistente virtual jurídico aprimorado"""
    
    def __init__(self):
        self.knowledge_base = EnhancedKnowledgeBase()
        self.classifier = QueryClassifier()
        self.response_generator = ResponseGenerator(self.knowledge_base)
        self.conversation_history = {}
    
    def process_query(self, query_text: str, user_id: str = "default", 
                     style: ResponseStyle = ResponseStyle.CONCISE) -> LegalResponse:
        """Processa consulta jurídica"""
        # Classifica a consulta
        query_type, confidence = self.classifier.classify_query(query_text)
        
        # Cria objeto de consulta
        query = LegalQuery(
            id=f"query_{int(time.time())}_{user_id}",
            text=query_text,
            type=query_type,
            context=self._get_conversation_context(user_id),
            user_id=user_id,
            timestamp=datetime.now()
        )
        
        # Gera resposta
        response = self.response_generator.generate_response(query, style)
        
        # Atualiza histórico da conversa
        self._update_conversation_history(user_id, query, response)
        
        logger.info(f"Consulta processada: {query_type.value} - Confiança: {confidence:.2f}")
        
        return response
    
    def _get_conversation_context(self, user_id: str) -> Dict[str, Any]:
        """Obtém contexto da conversa"""
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
        
        # Retorna últimas 3 interações
        recent_history = self.conversation_history[user_id][-3:]
        
        return {
            "previous_queries": [h["query"] for h in recent_history],
            "previous_topics": [h["query_type"] for h in recent_history]
        }
    
    def _update_conversation_history(self, user_id: str, query: LegalQuery, response: LegalResponse):
        """Atualiza histórico da conversa"""
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
        
        self.conversation_history[user_id].append({
            "query": query.text,
            "query_type": query.type.value,
            "response": response.answer,
            "timestamp": query.timestamp.isoformat()
        })
        
        # Mantém apenas últimas 10 interações
        if len(self.conversation_history[user_id]) > 10:
            self.conversation_history[user_id] = self.conversation_history[user_id][-10:]
    
    def get_conversation_summary(self, user_id: str) -> Dict[str, Any]:
        """Retorna resumo da conversa"""
        if user_id not in self.conversation_history:
            return {"message": "Nenhuma conversa encontrada"}
        
        history = self.conversation_history[user_id]
        
        return {
            "total_queries": len(history),
            "query_types": list(set(h["query_type"] for h in history)),
            "recent_topics": [h["query"] for h in history[-3:]],
            "first_interaction": history[0]["timestamp"] if history else None,
            "last_interaction": history[-1]["timestamp"] if history else None
        }
    
    def suggest_related_queries(self, query_text: str) -> List[str]:
        """Sugere consultas relacionadas"""
        query_lower = query_text.lower()
        suggestions = []
        
        # Sugestões baseadas em palavras-chave
        if "danos morais" in query_lower:
            suggestions.extend([
                "Como calcular valor de danos morais?",
                "Quais são os critérios para danos morais?",
                "Jurisprudência sobre danos morais por negativação"
            ])
        
        if "trabalhista" in query_lower or "rescisão" in query_lower:
            suggestions.extend([
                "Como calcular verbas rescisórias?",
                "Prazo para pagamento das verbas rescisórias",
                "Diferença entre demissão com e sem justa causa"
            ])
        
        if "contrato" in query_lower:
            suggestions.extend([
                "Como analisar cláusulas abusivas?",
                "Rescisão de contrato por inadimplemento",
                "Revisão de contrato por onerosidade excessiva"
            ])
        
        return suggestions[:5]  # Máximo 5 sugestões

def main():
    """Função principal para demonstração"""
    print("=== Assistente Virtual Jurídico - Versão Melhorada ===")
    
    # Cria instância do assistente
    assistant = EnhancedVirtualAssistant()
    
    # Consultas de exemplo
    consultas_exemplo = [
        "Como calcular danos morais por negativação indevida?",
        "Qual o prazo para contestação no processo civil?",
        "Quais são as verbas rescisórias devidas na demissão sem justa causa?",
        "Como funciona a inversão do ônus da prova no CDC?"
    ]
    
    print(f"\nProcessando {len(consultas_exemplo)} consultas de exemplo...")
    
    for i, consulta in enumerate(consultas_exemplo, 1):
        print(f"\n--- Consulta {i} ---")
        print(f"Pergunta: {consulta}")
        
        # Processa consulta
        response = assistant.process_query(consulta, "usuario_teste", ResponseStyle.CONCISE)
        
        print(f"Tipo: {response.query_id}")
        print(f"Resposta: {response.answer[:200]}...")
        print(f"Confiança: {response.confidence:.2f}")
        print(f"Tempo de resposta: {response.response_time:.2f}s")
        
        if response.sources:
            print(f"Fontes: {', '.join(response.sources[:3])}")
        
        if response.follow_up_questions:
            print(f"Perguntas relacionadas: {response.follow_up_questions[0]}")
    
    # Resumo da conversa
    summary = assistant.get_conversation_summary("usuario_teste")
    print(f"\n--- Resumo da Conversa ---")
    print(f"Total de consultas: {summary['total_queries']}")
    print(f"Tipos de consulta: {', '.join(summary['query_types'])}")
    
    # Sugestões relacionadas
    suggestions = assistant.suggest_related_queries("danos morais")
    print(f"\n--- Sugestões Relacionadas ---")
    for suggestion in suggestions[:3]:
        print(f"- {suggestion}")
    
    return assistant

if __name__ == "__main__":
    main()

