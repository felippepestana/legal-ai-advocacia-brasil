"""
Funcionalidades Avançadas de Pesquisa Inteligente
Implementa busca semântica, integração com múltiplas fontes e análise contextual
"""

import json
import re
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import requests
import time
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import openai

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SearchType(Enum):
    """Tipos de pesquisa"""
    JURISPRUDENCE = "Jurisprudência"
    LEGISLATION = "Legislação"
    DOCTRINE = "Doutrina"
    PRECEDENTS = "Precedentes"
    CASES = "Casos"
    MIXED = "Mista"

class SourceType(Enum):
    """Tipos de fonte de dados"""
    STJ = "Superior Tribunal de Justiça"
    STF = "Supremo Tribunal Federal"
    TST = "Tribunal Superior do Trabalho"
    TJSP = "Tribunal de Justiça de São Paulo"
    TJRJ = "Tribunal de Justiça do Rio de Janeiro"
    PLANALTO = "Planalto - Legislação"
    JUSBRASIL = "JusBrasil"
    CONJUR = "Consultor Jurídico"

@dataclass
class SearchResult:
    """Resultado de pesquisa"""
    id: str
    title: str
    content: str
    source: SourceType
    relevance_score: float
    date: datetime
    url: str
    metadata: Dict[str, Any]
    summary: str
    key_concepts: List[str]

@dataclass
class SemanticQuery:
    """Consulta semântica"""
    original_query: str
    expanded_terms: List[str]
    legal_concepts: List[str]
    intent: str
    context: Dict[str, Any]

class LegalKnowledgeBase:
    """Base de conhecimento jurídico"""
    
    def __init__(self):
        self.legal_concepts = self._load_legal_concepts()
        self.synonyms = self._load_legal_synonyms()
        self.precedents = self._load_precedents_database()
        
    def _load_legal_concepts(self) -> Dict[str, List[str]]:
        """Carrega conceitos jurídicos organizados por área"""
        return {
            "civil": [
                "responsabilidade civil", "danos morais", "danos materiais", "indenização",
                "contrato", "obrigação", "inadimplemento", "rescisão", "nulidade",
                "posse", "propriedade", "usucapião", "direitos reais"
            ],
            "trabalhista": [
                "rescisão", "justa causa", "aviso prévio", "FGTS", "13º salário",
                "férias", "horas extras", "adicional noturno", "insalubridade",
                "periculosidade", "estabilidade", "reintegração"
            ],
            "criminal": [
                "crime", "contravenção", "dolo", "culpa", "legítima defesa",
                "estado de necessidade", "prescrição", "decadência", "sursis",
                "livramento condicional", "prisão preventiva"
            ],
            "tributario": [
                "tributo", "imposto", "taxa", "contribuição", "ICMS", "IPI",
                "ISS", "IR", "COFINS", "PIS", "execução fiscal", "parcelamento"
            ],
            "processual": [
                "petição inicial", "contestação", "tréplica", "sentença", "acórdão",
                "recurso", "apelação", "agravo", "embargos", "execução",
                "cumprimento de sentença", "tutela antecipada"
            ]
        }
    
    def _load_legal_synonyms(self) -> Dict[str, List[str]]:
        """Carrega sinônimos jurídicos"""
        return {
            "danos morais": ["dano moral", "lesão extrapatrimonial", "dano imaterial"],
            "indenização": ["reparação", "ressarcimento", "compensação"],
            "contrato": ["pacto", "acordo", "convenção", "ajuste"],
            "rescisão": ["resolução", "extinção", "término"],
            "jurisprudência": ["precedente", "decisão judicial", "entendimento"],
            "legislação": ["lei", "norma", "dispositivo legal", "texto legal"],
            "tribunal": ["corte", "juízo", "instância judicial"]
        }
    
    def _load_precedents_database(self) -> List[Dict[str, Any]]:
        """Carrega base de precedentes simulada"""
        return [
            {
                "id": "stj_resp_1234567",
                "court": "STJ",
                "number": "REsp 1.234.567/SP",
                "date": "2024-03-15",
                "subject": "Danos morais por negativação indevida",
                "summary": "Configuração de danos morais independe de prova do prejuízo",
                "keywords": ["danos morais", "negativação", "in re ipsa"],
                "binding": True
            },
            {
                "id": "stf_re_987654",
                "court": "STF",
                "number": "RE 987.654/RJ",
                "date": "2024-02-20",
                "subject": "Prescrição em ação de cobrança",
                "summary": "Prazo prescricional de 5 anos para cobrança de honorários",
                "keywords": ["prescrição", "honorários", "cobrança"],
                "binding": True
            },
            {
                "id": "tst_rr_555888",
                "court": "TST",
                "number": "RR 555.888/MG",
                "date": "2024-01-10",
                "subject": "Horas extras e banco de horas",
                "summary": "Compensação de horas deve ser prévia e por acordo",
                "keywords": ["horas extras", "banco de horas", "compensação"],
                "binding": True
            }
        ]

class SemanticSearchEngine:
    """Motor de busca semântica"""
    
    def __init__(self):
        self.knowledge_base = LegalKnowledgeBase()
        self.vectorizer = TfidfVectorizer(max_features=5000, stop_words='english')
        self.openai_client = openai.OpenAI()
        self.document_vectors = None
        self.documents = []
        
    def _expand_query_semantically(self, query: str) -> SemanticQuery:
        """Expande consulta semanticamente"""
        # Identifica conceitos jurídicos na consulta
        legal_concepts = []
        for area, concepts in self.knowledge_base.legal_concepts.items():
            for concept in concepts:
                if concept.lower() in query.lower():
                    legal_concepts.append(concept)
        
        # Expande com sinônimos
        expanded_terms = [query]
        for term, synonyms in self.knowledge_base.synonyms.items():
            if term.lower() in query.lower():
                expanded_terms.extend(synonyms)
        
        # Determina intenção da consulta
        intent = self._classify_search_intent(query)
        
        return SemanticQuery(
            original_query=query,
            expanded_terms=expanded_terms,
            legal_concepts=legal_concepts,
            intent=intent,
            context={"timestamp": datetime.now().isoformat()}
        )
    
    def _classify_search_intent(self, query: str) -> str:
        """Classifica a intenção da pesquisa"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["como", "quando", "onde", "por que"]):
            return "informational"
        elif any(word in query_lower for word in ["calcular", "valor", "prazo"]):
            return "computational"
        elif any(word in query_lower for word in ["jurisprudência", "precedente", "decisão"]):
            return "jurisprudential"
        elif any(word in query_lower for word in ["lei", "artigo", "código"]):
            return "legislative"
        else:
            return "general"
    
    def search_with_ai_enhancement(self, query: str, search_type: SearchType = SearchType.MIXED,
                                  max_results: int = 10) -> List[SearchResult]:
        """Realiza busca com melhorias de IA"""
        logger.info(f"Executando pesquisa semântica: {query}")
        
        # Expande consulta semanticamente
        semantic_query = self._expand_query_semantically(query)
        
        # Busca em múltiplas fontes
        results = []
        
        # Busca em precedentes
        precedent_results = self._search_precedents(semantic_query)
        results.extend(precedent_results)
        
        # Busca em jurisprudência simulada
        jurisprudence_results = self._search_jurisprudence(semantic_query)
        results.extend(jurisprudence_results)
        
        # Busca em legislação simulada
        legislation_results = self._search_legislation(semantic_query)
        results.extend(legislation_results)
        
        # Ordena por relevância
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        
        # Aplica pós-processamento com IA
        enhanced_results = self._enhance_results_with_ai(results[:max_results], semantic_query)
        
        logger.info(f"Pesquisa concluída: {len(enhanced_results)} resultados")
        return enhanced_results
    
    def _search_precedents(self, semantic_query: SemanticQuery) -> List[SearchResult]:
        """Busca em base de precedentes"""
        results = []
        
        for precedent in self.knowledge_base.precedents:
            # Calcula relevância baseada em palavras-chave
            relevance = self._calculate_precedent_relevance(precedent, semantic_query)
            
            if relevance > 0.3:  # Threshold mínimo
                result = SearchResult(
                    id=precedent["id"],
                    title=f"{precedent['number']} - {precedent['subject']}",
                    content=precedent["summary"],
                    source=SourceType.STJ if precedent["court"] == "STJ" else SourceType.STF,
                    relevance_score=relevance,
                    date=datetime.strptime(precedent["date"], "%Y-%m-%d"),
                    url=f"https://exemplo.com/{precedent['id']}",
                    metadata={
                        "court": precedent["court"],
                        "number": precedent["number"],
                        "binding": precedent["binding"]
                    },
                    summary=precedent["summary"],
                    key_concepts=precedent["keywords"]
                )
                results.append(result)
        
        return results
    
    def _calculate_precedent_relevance(self, precedent: Dict[str, Any], 
                                     semantic_query: SemanticQuery) -> float:
        """Calcula relevância de um precedente"""
        score = 0.0
        
        # Pontuação por palavras-chave
        for keyword in precedent["keywords"]:
            if keyword.lower() in semantic_query.original_query.lower():
                score += 0.3
            for expanded_term in semantic_query.expanded_terms:
                if keyword.lower() in expanded_term.lower():
                    score += 0.2
        
        # Pontuação por conceitos jurídicos
        for concept in semantic_query.legal_concepts:
            if concept.lower() in precedent["summary"].lower():
                score += 0.4
        
        # Bonificação para precedentes vinculantes
        if precedent.get("binding", False):
            score += 0.2
        
        return min(score, 1.0)
    
    def _search_jurisprudence(self, semantic_query: SemanticQuery) -> List[SearchResult]:
        """Busca em jurisprudência simulada"""
        # Simulação de resultados de jurisprudência
        jurisprudence_data = [
            {
                "id": "tjsp_apelacao_123456",
                "title": "Apelação Cível nº 1234567-89.2024.8.26.0100",
                "content": "Ação de indenização por danos morais. Negativação indevida. Dano moral configurado. Quantum indenizatório fixado em R$ 10.000,00.",
                "court": "TJSP",
                "date": "2024-03-01",
                "keywords": ["danos morais", "negativação", "indenização"]
            },
            {
                "id": "tjrj_apelacao_789012",
                "title": "Apelação Cível nº 7890123-45.2024.8.19.0001",
                "content": "Rescisão contratual. Inadimplemento. Multa contratual aplicável. Procedência do pedido.",
                "court": "TJRJ",
                "date": "2024-02-15",
                "keywords": ["rescisão", "inadimplemento", "multa"]
            }
        ]
        
        results = []
        for item in jurisprudence_data:
            relevance = self._calculate_text_relevance(item["content"], semantic_query)
            
            if relevance > 0.2:
                result = SearchResult(
                    id=item["id"],
                    title=item["title"],
                    content=item["content"],
                    source=SourceType.TJSP if item["court"] == "TJSP" else SourceType.TJRJ,
                    relevance_score=relevance,
                    date=datetime.strptime(item["date"], "%Y-%m-%d"),
                    url=f"https://exemplo.com/{item['id']}",
                    metadata={"court": item["court"]},
                    summary=item["content"][:200] + "...",
                    key_concepts=item["keywords"]
                )
                results.append(result)
        
        return results
    
    def _search_legislation(self, semantic_query: SemanticQuery) -> List[SearchResult]:
        """Busca em legislação simulada"""
        legislation_data = [
            {
                "id": "cc_art_927",
                "title": "Código Civil - Art. 927",
                "content": "Aquele que, por ato ilícito (arts. 186 e 187), causar dano a outrem, fica obrigado a repará-lo.",
                "law": "Código Civil",
                "article": "927",
                "keywords": ["responsabilidade civil", "dano", "reparação"]
            },
            {
                "id": "cdc_art_14",
                "title": "Código de Defesa do Consumidor - Art. 14",
                "content": "O fornecedor de serviços responde, independentemente da existência de culpa, pela reparação dos danos causados aos consumidores.",
                "law": "CDC",
                "article": "14",
                "keywords": ["responsabilidade", "consumidor", "fornecedor"]
            }
        ]
        
        results = []
        for item in legislation_data:
            relevance = self._calculate_text_relevance(item["content"], semantic_query)
            
            if relevance > 0.2:
                result = SearchResult(
                    id=item["id"],
                    title=item["title"],
                    content=item["content"],
                    source=SourceType.PLANALTO,
                    relevance_score=relevance,
                    date=datetime(2002, 1, 10),  # Data fictícia
                    url=f"https://planalto.gov.br/{item['id']}",
                    metadata={
                        "law": item["law"],
                        "article": item["article"]
                    },
                    summary=item["content"],
                    key_concepts=item["keywords"]
                )
                results.append(result)
        
        return results
    
    def _calculate_text_relevance(self, text: str, semantic_query: SemanticQuery) -> float:
        """Calcula relevância de um texto"""
        score = 0.0
        text_lower = text.lower()
        
        # Pontuação por consulta original
        if semantic_query.original_query.lower() in text_lower:
            score += 0.5
        
        # Pontuação por termos expandidos
        for term in semantic_query.expanded_terms:
            if term.lower() in text_lower:
                score += 0.2
        
        # Pontuação por conceitos jurídicos
        for concept in semantic_query.legal_concepts:
            if concept.lower() in text_lower:
                score += 0.3
        
        return min(score, 1.0)
    
    def _enhance_results_with_ai(self, results: List[SearchResult], 
                                semantic_query: SemanticQuery) -> List[SearchResult]:
        """Melhora resultados usando IA"""
        try:
            # Gera resumos mais relevantes usando IA
            for result in results:
                if len(result.content) > 200:
                    enhanced_summary = self._generate_ai_summary(result.content, semantic_query)
                    if enhanced_summary:
                        result.summary = enhanced_summary
                
                # Extrai conceitos-chave usando IA
                enhanced_concepts = self._extract_key_concepts_ai(result.content)
                if enhanced_concepts:
                    result.key_concepts.extend(enhanced_concepts)
                    result.key_concepts = list(set(result.key_concepts))  # Remove duplicatas
        
        except Exception as e:
            logger.warning(f"Erro na melhoria por IA: {e}")
        
        return results
    
    def _generate_ai_summary(self, content: str, semantic_query: SemanticQuery) -> Optional[str]:
        """Gera resumo usando IA"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "Você é um especialista em direito. Crie um resumo conciso e relevante do texto jurídico fornecido, focando nos aspectos mais importantes para a consulta do usuário."
                    },
                    {
                        "role": "user",
                        "content": f"Consulta: {semantic_query.original_query}\n\nTexto: {content[:1000]}\n\nResumo:"
                    }
                ],
                max_tokens=150
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            logger.error(f"Erro na geração de resumo: {e}")
            return None
    
    def _extract_key_concepts_ai(self, content: str) -> List[str]:
        """Extrai conceitos-chave usando IA"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "Extraia os 3-5 conceitos jurídicos mais importantes do texto. Responda apenas com uma lista separada por vírgulas."
                    },
                    {
                        "role": "user",
                        "content": content[:800]
                    }
                ],
                max_tokens=100
            )
            
            concepts_text = response.choices[0].message.content.strip()
            concepts = [c.strip() for c in concepts_text.split(',')]
            return concepts[:5]  # Máximo 5 conceitos
        
        except Exception as e:
            logger.error(f"Erro na extração de conceitos: {e}")
            return []

class AdvancedSearchInterface:
    """Interface avançada de pesquisa"""
    
    def __init__(self):
        self.search_engine = SemanticSearchEngine()
        self.search_history = []
        
    def search(self, query: str, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Realiza pesquisa avançada"""
        filters = filters or {}
        
        # Registra pesquisa no histórico
        search_record = {
            "query": query,
            "timestamp": datetime.now(),
            "filters": filters
        }
        self.search_history.append(search_record)
        
        # Determina tipo de pesquisa
        search_type_str = filters.get("type", "MIXED")
        if search_type_str == "MIXED":
            search_type = SearchType.MIXED
        elif search_type_str == "JURISPRUDENCE":
            search_type = SearchType.JURISPRUDENCE
        elif search_type_str == "LEGISLATION":
            search_type = SearchType.LEGISLATION
        else:
            search_type = SearchType.MIXED
        
        # Executa pesquisa
        results = self.search_engine.search_with_ai_enhancement(
            query, 
            search_type, 
            filters.get("max_results", 10)
        )
        
        # Aplica filtros adicionais
        filtered_results = self._apply_filters(results, filters)
        
        # Gera sugestões relacionadas
        suggestions = self._generate_related_suggestions(query)
        
        return {
            "query": query,
            "results": [asdict(r) for r in filtered_results],
            "total_results": len(filtered_results),
            "suggestions": suggestions,
            "search_time": 0.5,  # Simulado
            "filters_applied": filters
        }
    
    def _apply_filters(self, results: List[SearchResult], filters: Dict[str, Any]) -> List[SearchResult]:
        """Aplica filtros aos resultados"""
        filtered = results
        
        # Filtro por fonte
        if "sources" in filters:
            allowed_sources = [SourceType(s) for s in filters["sources"]]
            filtered = [r for r in filtered if r.source in allowed_sources]
        
        # Filtro por data
        if "date_from" in filters:
            date_from = datetime.strptime(filters["date_from"], "%Y-%m-%d")
            filtered = [r for r in filtered if r.date >= date_from]
        
        if "date_to" in filters:
            date_to = datetime.strptime(filters["date_to"], "%Y-%m-%d")
            filtered = [r for r in filtered if r.date <= date_to]
        
        # Filtro por relevância mínima
        if "min_relevance" in filters:
            min_relevance = float(filters["min_relevance"])
            filtered = [r for r in filtered if r.relevance_score >= min_relevance]
        
        return filtered
    
    def _generate_related_suggestions(self, query: str) -> List[str]:
        """Gera sugestões relacionadas"""
        # Implementação simplificada
        suggestions = []
        
        query_lower = query.lower()
        
        if "danos morais" in query_lower:
            suggestions.extend([
                "valor indenização danos morais",
                "danos morais negativação",
                "danos morais pessoa jurídica"
            ])
        
        if "contrato" in query_lower:
            suggestions.extend([
                "rescisão contratual",
                "inadimplemento contratual",
                "cláusulas abusivas"
            ])
        
        if "trabalhista" in query_lower:
            suggestions.extend([
                "rescisão trabalhista",
                "horas extras",
                "verbas rescisórias"
            ])
        
        return suggestions[:5]
    
    def get_search_analytics(self) -> Dict[str, Any]:
        """Retorna analytics das pesquisas"""
        if not self.search_history:
            return {"message": "Nenhuma pesquisa realizada ainda"}
        
        # Consultas mais frequentes
        query_counts = {}
        for search in self.search_history:
            query = search["query"].lower()
            query_counts[query] = query_counts.get(query, 0) + 1
        
        most_frequent = sorted(query_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Padrões temporais
        recent_searches = [s for s in self.search_history if 
                          (datetime.now() - s["timestamp"]).days <= 7]
        
        return {
            "total_searches": len(self.search_history),
            "recent_searches": len(recent_searches),
            "most_frequent_queries": most_frequent,
            "average_searches_per_day": len(recent_searches) / 7,
            "last_search": self.search_history[-1]["timestamp"].isoformat()
        }

def main():
    """Função principal para demonstração"""
    print("=== Funcionalidades Avançadas de Pesquisa Inteligente ===")
    
    # Cria interface de pesquisa avançada
    search_interface = AdvancedSearchInterface()
    
    # Consultas de exemplo
    consultas_exemplo = [
        "danos morais por negativação indevida",
        "rescisão contratual por inadimplemento",
        "horas extras banco de horas",
        "prescrição ação de cobrança"
    ]
    
    print(f"\nExecutando {len(consultas_exemplo)} pesquisas de exemplo...")
    
    for i, consulta in enumerate(consultas_exemplo, 1):
        print(f"\n--- Pesquisa {i}: {consulta} ---")
        
        # Executa pesquisa
        resultado = search_interface.search(
            consulta,
            {
                "type": "MIXED",
                "max_results": 5,
                "min_relevance": 0.3
            }
        )
        
        print(f"Resultados encontrados: {resultado['total_results']}")
        print(f"Tempo de pesquisa: {resultado['search_time']}s")
        
        # Mostra primeiros resultados
        for j, result in enumerate(resultado['results'][:2], 1):
            print(f"  {j}. {result['title']}")
            print(f"     Relevância: {result['relevance_score']:.2f}")
            print(f"     Fonte: {result['source']}")
            print(f"     Conceitos: {', '.join(result['key_concepts'][:3])}")
        
        # Mostra sugestões
        if resultado['suggestions']:
            print(f"  Sugestões: {', '.join(resultado['suggestions'][:3])}")
    
    # Analytics de pesquisa
    print(f"\n--- Analytics de Pesquisa ---")
    analytics = search_interface.get_search_analytics()
    print(f"Total de pesquisas: {analytics['total_searches']}")
    print(f"Pesquisas recentes: {analytics['recent_searches']}")
    print(f"Consultas mais frequentes:")
    for query, count in analytics['most_frequent_queries'][:3]:
        print(f"  - '{query}': {count} vezes")
    
    return search_interface

if __name__ == "__main__":
    main()

