#!/usr/bin/env python3
"""
Sistema de Pesquisa Jurídica Inteligente
Busca avançada em jurisprudência, legislação e doutrina com IA e processamento de linguagem natural.
"""

import os
import json
import uuid
import logging
import re
from datetime import datetime, date
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import requests
from urllib.parse import quote_plus
import time

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SearchType(Enum):
    JURISPRUDENCIA = "jurisprudencia"
    LEGISLACAO = "legislacao"
    DOUTRINA = "doutrina"
    SUMULAS = "sumulas"
    PRECEDENTES = "precedentes"
    TODOS = "todos"

class CourtLevel(Enum):
    STF = "stf"
    STJ = "stj"
    TST = "tst"
    TSE = "tse"
    STM = "stm"
    TJ = "tj"
    TRF = "trf"
    TRT = "trt"
    TRE = "tre"
    TODOS = "todos"

class SearchRelevance(Enum):
    MUITO_ALTA = "muito_alta"
    ALTA = "alta"
    MEDIA = "media"
    BAIXA = "baixa"

@dataclass
class SearchQuery:
    query_id: str
    original_query: str
    processed_query: str
    search_type: SearchType
    court_level: Optional[CourtLevel]
    date_range: Optional[Tuple[date, date]]
    keywords: List[str]
    legal_concepts: List[str]
    created_at: datetime

@dataclass
class SearchResult:
    result_id: str
    title: str
    summary: str
    full_text: str
    source: str
    court: str
    date_published: Optional[date]
    relevance_score: float
    relevance_level: SearchRelevance
    url: Optional[str]
    case_number: Optional[str]
    keywords_found: List[str]
    legal_concepts_found: List[str]

@dataclass
class SearchSession:
    session_id: str
    user_id: str
    queries: List[SearchQuery]
    results: List[SearchResult]
    created_at: datetime
    updated_at: datetime

class LegalConceptExtractor:
    """Extrator de conceitos jurídicos de consultas em linguagem natural."""
    
    def __init__(self):
        # Dicionário de conceitos jurídicos e suas variações
        self.legal_concepts = {
            "danos_morais": ["danos morais", "dano moral", "indenização moral", "sofrimento psíquico"],
            "responsabilidade_civil": ["responsabilidade civil", "responsabilização", "culpa civil"],
            "direito_consumidor": ["direito do consumidor", "cdc", "código de defesa do consumidor", "relação de consumo"],
            "contrato": ["contrato", "contratual", "obrigação contratual", "cláusula"],
            "trabalhista": ["direito do trabalho", "trabalhista", "clt", "empregado", "empregador"],
            "familia": ["direito de família", "divórcio", "pensão alimentícia", "guarda"],
            "tributario": ["direito tributário", "imposto", "tributo", "icms", "ipi", "ir"],
            "criminal": ["direito penal", "crime", "delito", "contravenção"],
            "administrativo": ["direito administrativo", "servidor público", "licitação"],
            "constitucional": ["direito constitucional", "constituição", "inconstitucionalidade"],
            "processual": ["processo", "processual", "cpc", "procedimento"],
            "execucao": ["execução", "executivo", "penhora", "arrematação"],
            "recurso": ["recurso", "apelação", "agravo", "embargos"],
            "prescricao": ["prescrição", "decadência", "prazo prescricional"],
            "juros": ["juros", "correção monetária", "atualização"],
            "honorarios": ["honorários", "sucumbência", "custas processuais"]
        }
        
        # Padrões para identificação de números de processos
        self.process_patterns = [
            r'\b\d{7}-?\d{2}\.?\d{4}\.?\d{1}\.?\d{2}\.?\d{4}\b',  # Padrão CNJ
            r'\b\d{6,8}\.?\d{4}\.?\d{3}\.?\d{4}\b'  # Padrão antigo
        ]
    
    def extract_concepts(self, query: str) -> Tuple[List[str], List[str]]:
        """Extrai conceitos jurídicos e palavras-chave de uma consulta."""
        query_lower = query.lower()
        
        # Extrair conceitos jurídicos
        found_concepts = []
        for concept, variations in self.legal_concepts.items():
            for variation in variations:
                if variation in query_lower:
                    found_concepts.append(concept)
                    break
        
        # Extrair palavras-chave (palavras importantes que não são stop words)
        stop_words = {
            "o", "a", "os", "as", "um", "uma", "uns", "umas", "de", "da", "do", "das", "dos",
            "em", "na", "no", "nas", "nos", "para", "por", "com", "sem", "sobre", "sob",
            "entre", "até", "desde", "durante", "através", "mediante", "conforme", "segundo",
            "e", "ou", "mas", "porém", "contudo", "entretanto", "todavia", "não", "sim",
            "que", "qual", "quais", "quando", "onde", "como", "porque", "se", "caso"
        }
        
        # Limpar e dividir a consulta
        words = re.findall(r'\b[a-záàâãéèêíìîóòôõúùûç]+\b', query_lower)
        keywords = [word for word in words if len(word) > 2 and word not in stop_words]
        
        # Remover duplicatas mantendo ordem
        keywords = list(dict.fromkeys(keywords))
        found_concepts = list(dict.fromkeys(found_concepts))
        
        return found_concepts, keywords
    
    def extract_process_numbers(self, query: str) -> List[str]:
        """Extrai números de processos da consulta."""
        process_numbers = []
        for pattern in self.process_patterns:
            matches = re.findall(pattern, query)
            process_numbers.extend(matches)
        
        return list(set(process_numbers))  # Remover duplicatas

class JurisprudenceSearchEngine:
    """Motor de busca de jurisprudência com integração a fontes oficiais."""
    
    def __init__(self):
        self.concept_extractor = LegalConceptExtractor()
        
        # URLs base dos tribunais (simuladas para demonstração)
        self.court_apis = {
            CourtLevel.STJ: "https://scon.stj.jus.br/SCON/",
            CourtLevel.STF: "https://portal.stf.jus.br/",
            CourtLevel.TST: "https://jurisprudencia.tst.jus.br/",
            # Adicionar outras URLs conforme disponibilidade
        }
        
        # Base de dados simulada de jurisprudência
        self._initialize_sample_jurisprudence()
    
    def _initialize_sample_jurisprudence(self):
        """Inicializa base de dados simulada com jurisprudência de exemplo."""
        self.sample_jurisprudence = [
            {
                "title": "REsp 1.234.567/SP - Danos Morais em Relação de Consumo",
                "summary": "Configuração de danos morais em relação de consumo. Inscrição indevida em órgãos de proteção ao crédito.",
                "full_text": "RECURSO ESPECIAL. DIREITO DO CONSUMIDOR. DANOS MORAIS. INSCRIÇÃO INDEVIDA. VALOR DA INDENIZAÇÃO. O Superior Tribunal de Justiça tem entendimento consolidado no sentido de que a inscrição indevida do nome do consumidor em órgãos de proteção ao crédito configura dano moral in re ipsa, dispensando a prova do prejuízo. O valor da indenização deve observar os princípios da proporcionalidade e razoabilidade.",
                "source": "STJ",
                "court": "Superior Tribunal de Justiça",
                "date_published": date(2024, 3, 15),
                "case_number": "REsp 1.234.567/SP",
                "url": "https://stj.jus.br/exemplo1",
                "keywords": ["danos", "morais", "consumidor", "inscrição", "indevida"],
                "concepts": ["danos_morais", "direito_consumidor"]
            },
            {
                "title": "Súmula 297 do STJ - CDC e Instituições Financeiras",
                "summary": "Aplicabilidade do Código de Defesa do Consumidor às instituições financeiras.",
                "full_text": "O Código de Defesa do Consumidor é aplicável às instituições financeiras. Esta súmula pacificou o entendimento sobre a aplicação das normas consumeristas aos contratos bancários e financeiros.",
                "source": "STJ",
                "court": "Superior Tribunal de Justiça",
                "date_published": date(2004, 9, 22),
                "case_number": "Súmula 297",
                "url": "https://stj.jus.br/sumula297",
                "keywords": ["cdc", "instituições", "financeiras", "bancos"],
                "concepts": ["direito_consumidor", "contrato"]
            },
            {
                "title": "AgRg no AREsp 987.654/RJ - Honorários Advocatícios",
                "summary": "Fixação de honorários advocatícios. Critérios do art. 85 do CPC.",
                "full_text": "AGRAVO REGIMENTAL. HONORÁRIOS ADVOCATÍCIOS. FIXAÇÃO. ART. 85 DO CPC. A fixação dos honorários advocatícios deve observar os critérios estabelecidos no art. 85 do Código de Processo Civil, considerando o grau de zelo do profissional, o lugar de prestação do serviço, a natureza e importância da causa, o trabalho realizado pelo advogado e o tempo exigido para o seu serviço.",
                "source": "STJ",
                "court": "Superior Tribunal de Justiça",
                "date_published": date(2024, 1, 10),
                "case_number": "AgRg no AREsp 987.654/RJ",
                "url": "https://stj.jus.br/exemplo2",
                "keywords": ["honorários", "advocatícios", "fixação", "cpc"],
                "concepts": ["honorarios", "processual"]
            },
            {
                "title": "REsp 2.345.678/MG - Responsabilidade Civil Médica",
                "summary": "Responsabilidade civil do médico. Obrigação de meio vs. obrigação de resultado.",
                "full_text": "RESPONSABILIDADE CIVIL. ERRO MÉDICO. OBRIGAÇÃO DE MEIO. A responsabilidade civil do médico, em regra, é subjetiva, decorrente da violação de uma obrigação de meio, e não de resultado. Deve ser demonstrada a culpa do profissional para configuração do dever de indenizar.",
                "source": "STJ",
                "court": "Superior Tribunal de Justiça",
                "date_published": date(2024, 2, 28),
                "case_number": "REsp 2.345.678/MG",
                "url": "https://stj.jus.br/exemplo3",
                "keywords": ["responsabilidade", "civil", "médico", "erro", "culpa"],
                "concepts": ["responsabilidade_civil"]
            }
        ]
    
    def search_jurisprudence(self, query: str, search_type: SearchType = SearchType.JURISPRUDENCIA,
                           court_level: Optional[CourtLevel] = None,
                           date_range: Optional[Tuple[date, date]] = None,
                           max_results: int = 10) -> Tuple[SearchQuery, List[SearchResult]]:
        """Realiza busca de jurisprudência."""
        
        # Processar consulta
        concepts, keywords = self.concept_extractor.extract_concepts(query)
        process_numbers = self.concept_extractor.extract_process_numbers(query)
        
        # Criar objeto de consulta
        search_query = SearchQuery(
            query_id=str(uuid.uuid4()),
            original_query=query,
            processed_query=self._process_query(query, concepts, keywords),
            search_type=search_type,
            court_level=court_level,
            date_range=date_range,
            keywords=keywords,
            legal_concepts=concepts,
            created_at=datetime.now()
        )
        
        # Realizar busca
        results = self._perform_search(search_query, max_results)
        
        logger.info(f"Busca realizada: '{query}' - {len(results)} resultados encontrados")
        return search_query, results
    
    def _process_query(self, query: str, concepts: List[str], keywords: List[str]) -> str:
        """Processa a consulta para otimizar a busca."""
        # Expandir conceitos jurídicos
        expanded_terms = []
        
        for concept in concepts:
            if concept in self.concept_extractor.legal_concepts:
                expanded_terms.extend(self.concept_extractor.legal_concepts[concept])
        
        # Combinar termos originais com expansões
        all_terms = keywords + expanded_terms
        processed_query = " ".join(set(all_terms))  # Remover duplicatas
        
        return processed_query
    
    def _perform_search(self, search_query: SearchQuery, max_results: int) -> List[SearchResult]:
        """Executa a busca na base de dados."""
        results = []
        
        # Buscar na base simulada
        for item in self.sample_jurisprudence:
            relevance_score = self._calculate_relevance(search_query, item)
            
            if relevance_score > 0.1:  # Threshold mínimo de relevância
                # Filtrar por tribunal se especificado
                if search_query.court_level and search_query.court_level != CourtLevel.TODOS:
                    if search_query.court_level.value.upper() not in item["source"]:
                        continue
                
                # Filtrar por data se especificado
                if search_query.date_range and item["date_published"]:
                    start_date, end_date = search_query.date_range
                    if not (start_date <= item["date_published"] <= end_date):
                        continue
                
                # Determinar nível de relevância
                if relevance_score >= 0.8:
                    relevance_level = SearchRelevance.MUITO_ALTA
                elif relevance_score >= 0.6:
                    relevance_level = SearchRelevance.ALTA
                elif relevance_score >= 0.4:
                    relevance_level = SearchRelevance.MEDIA
                else:
                    relevance_level = SearchRelevance.BAIXA
                
                result = SearchResult(
                    result_id=str(uuid.uuid4()),
                    title=item["title"],
                    summary=item["summary"],
                    full_text=item["full_text"],
                    source=item["source"],
                    court=item["court"],
                    date_published=item["date_published"],
                    relevance_score=relevance_score,
                    relevance_level=relevance_level,
                    url=item["url"],
                    case_number=item["case_number"],
                    keywords_found=self._find_matching_keywords(search_query.keywords, item["keywords"]),
                    legal_concepts_found=self._find_matching_concepts(search_query.legal_concepts, item["concepts"])
                )
                
                results.append(result)
        
        # Ordenar por relevância
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        
        return results[:max_results]
    
    def _calculate_relevance(self, search_query: SearchQuery, item: Dict[str, Any]) -> float:
        """Calcula a relevância de um item para a consulta."""
        score = 0.0
        
        # Pontuação por palavras-chave encontradas
        matching_keywords = self._find_matching_keywords(search_query.keywords, item["keywords"])
        if search_query.keywords:
            keyword_score = len(matching_keywords) / len(search_query.keywords)
            score += keyword_score * 0.4
        
        # Pontuação por conceitos jurídicos
        matching_concepts = self._find_matching_concepts(search_query.legal_concepts, item["concepts"])
        if search_query.legal_concepts:
            concept_score = len(matching_concepts) / len(search_query.legal_concepts)
            score += concept_score * 0.6
        
        # Pontuação por presença no título (mais relevante)
        title_lower = item["title"].lower()
        for keyword in search_query.keywords:
            if keyword in title_lower:
                score += 0.2
        
        # Pontuação por presença no texto completo
        text_lower = item["full_text"].lower()
        for keyword in search_query.keywords:
            if keyword in text_lower:
                score += 0.1
        
        return min(score, 1.0)  # Limitar a 1.0
    
    def _find_matching_keywords(self, query_keywords: List[str], item_keywords: List[str]) -> List[str]:
        """Encontra palavras-chave que coincidem."""
        return [kw for kw in query_keywords if any(kw in item_kw for item_kw in item_keywords)]
    
    def _find_matching_concepts(self, query_concepts: List[str], item_concepts: List[str]) -> List[str]:
        """Encontra conceitos jurídicos que coincidem."""
        return [concept for concept in query_concepts if concept in item_concepts]

class IntelligentSearchManager:
    """Gerenciador principal do sistema de pesquisa inteligente."""
    
    def __init__(self):
        self.search_engine = JurisprudenceSearchEngine()
        self.search_sessions: Dict[str, SearchSession] = {}
    
    def create_search_session(self, user_id: str) -> str:
        """Cria uma nova sessão de pesquisa."""
        session_id = str(uuid.uuid4())
        
        session = SearchSession(
            session_id=session_id,
            user_id=user_id,
            queries=[],
            results=[],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.search_sessions[session_id] = session
        logger.info(f"Sessão de pesquisa criada: {session_id}")
        return session_id
    
    def perform_intelligent_search(self, session_id: str, query: str, 
                                 search_type: SearchType = SearchType.JURISPRUDENCIA,
                                 court_level: Optional[CourtLevel] = None,
                                 date_range: Optional[Tuple[date, date]] = None) -> List[SearchResult]:
        """Realiza uma pesquisa inteligente."""
        session = self.search_sessions.get(session_id)
        if not session:
            raise ValueError(f"Sessão {session_id} não encontrada")
        
        # Realizar busca
        search_query, results = self.search_engine.search_jurisprudence(
            query, search_type, court_level, date_range
        )
        
        # Adicionar à sessão
        session.queries.append(search_query)
        session.results.extend(results)
        session.updated_at = datetime.now()
        
        return results
    
    def get_search_suggestions(self, partial_query: str) -> List[str]:
        """Gera sugestões de pesquisa baseadas na consulta parcial."""
        suggestions = []
        
        # Sugestões baseadas em conceitos jurídicos
        concepts = self.search_engine.concept_extractor.legal_concepts
        for concept, variations in concepts.items():
            for variation in variations:
                if partial_query.lower() in variation.lower():
                    suggestions.append(variation)
        
        # Sugestões de consultas comuns
        common_queries = [
            "danos morais por inscrição indevida",
            "responsabilidade civil médica",
            "honorários advocatícios fixação",
            "CDC instituições financeiras",
            "prescrição direito do consumidor",
            "juros abusivos contrato bancário",
            "execução de título extrajudicial",
            "recurso de apelação prazo"
        ]
        
        for common_query in common_queries:
            if partial_query.lower() in common_query.lower():
                suggestions.append(common_query)
        
        return suggestions[:5]  # Limitar a 5 sugestões
    
    def get_related_searches(self, query: str) -> List[str]:
        """Gera pesquisas relacionadas baseadas na consulta atual."""
        concepts, keywords = self.search_engine.concept_extractor.extract_concepts(query)
        
        related_searches = []
        
        # Pesquisas relacionadas por conceito
        concept_relations = {
            "danos_morais": ["valor indenização danos morais", "prova danos morais", "danos morais coletivos"],
            "direito_consumidor": ["vício produto CDC", "publicidade enganosa", "direito arrependimento"],
            "responsabilidade_civil": ["nexo causal", "culpa exclusiva vítima", "caso fortuito força maior"],
            "contrato": ["cláusula abusiva", "revisão contratual", "resolução contrato"],
            "honorarios": ["honorários sucumbência", "honorários contratuais", "honorários execução"]
        }
        
        for concept in concepts:
            if concept in concept_relations:
                related_searches.extend(concept_relations[concept])
        
        # Pesquisas relacionadas por palavras-chave
        if "indenização" in keywords:
            related_searches.append("quantum indenizatório")
        if "contrato" in keywords:
            related_searches.append("teoria da imprevisão")
        if "banco" in keywords:
            related_searches.append("tarifa bancária abusiva")
        
        return related_searches[:3]  # Limitar a 3 sugestões
    
    def export_search_session(self, session_id: str, output_path: str):
        """Exporta uma sessão de pesquisa para arquivo."""
        session = self.search_sessions.get(session_id)
        if not session:
            raise ValueError(f"Sessão {session_id} não encontrada")
        
        # Converter para dicionário
        session_dict = asdict(session)
        
        # Converter enums e datas
        session_dict['created_at'] = session.created_at.isoformat()
        session_dict['updated_at'] = session.updated_at.isoformat()
        
        for query in session_dict['queries']:
            query['search_type'] = SearchType(query['search_type']).value
            query['created_at'] = datetime.fromisoformat(query['created_at']).isoformat()
            if query['court_level']:
                query['court_level'] = CourtLevel(query['court_level']).value
            if query['date_range']:
                query['date_range'] = [d.isoformat() if isinstance(d, date) else d for d in query['date_range']]
        
        for result in session_dict['results']:
            result['relevance_level'] = SearchRelevance(result['relevance_level']).value
            if result['date_published']:
                result['date_published'] = result['date_published'].isoformat()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(session_dict, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Sessão de pesquisa exportada para: {output_path}")

def main():
    """Função principal para demonstração."""
    search_manager = IntelligentSearchManager()
    
    print("=== SISTEMA DE PESQUISA JURÍDICA INTELIGENTE ===")
    
    # Criar sessão de pesquisa
    session_id = search_manager.create_search_session("usuario_demo")
    print(f"Sessão criada: {session_id}")
    
    # Consultas de exemplo
    queries = [
        "danos morais por inscrição indevida no SPC",
        "responsabilidade civil do médico por erro",
        "honorários advocatícios em execução",
        "CDC aplicável a bancos"
    ]
    
    for query in queries:
        print(f"\n--- Pesquisa: '{query}' ---")
        
        # Realizar pesquisa
        results = search_manager.perform_intelligent_search(session_id, query)
        
        print(f"Resultados encontrados: {len(results)}")
        
        # Exibir primeiros resultados
        for i, result in enumerate(results[:2], 1):
            print(f"\n{i}. {result.title}")
            print(f"   Relevância: {result.relevance_level.value} ({result.relevance_score:.2f})")
            print(f"   Tribunal: {result.source}")
            print(f"   Data: {result.date_published.strftime('%d/%m/%Y') if result.date_published else 'N/A'}")
            print(f"   Resumo: {result.summary[:100]}...")
            print(f"   Conceitos: {', '.join(result.legal_concepts_found)}")
        
        # Pesquisas relacionadas
        related = search_manager.get_related_searches(query)
        if related:
            print(f"\n   Pesquisas relacionadas: {', '.join(related)}")
    
    # Testar sugestões
    print(f"\n--- Sugestões para 'danos' ---")
    suggestions = search_manager.get_search_suggestions("danos")
    for suggestion in suggestions:
        print(f"  - {suggestion}")
    
    # Exportar sessão
    export_path = "/home/ubuntu/sessao_pesquisa_exemplo.json"
    search_manager.export_search_session(session_id, export_path)
    
    # Estatísticas da sessão
    session = search_manager.search_sessions[session_id]
    print(f"\n--- Estatísticas da Sessão ---")
    print(f"Total de consultas: {len(session.queries)}")
    print(f"Total de resultados: {len(session.results)}")
    print(f"Duração: {session.updated_at - session.created_at}")
    
    print(f"\nSessão exportada para: {export_path}")

if __name__ == "__main__":
    main()

