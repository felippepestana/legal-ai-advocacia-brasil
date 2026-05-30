#!/usr/bin/env python3
"""
Pesquisa Jurídica Inteligente - Versão Melhorada
Implementa melhorias: algoritmos de busca refinados, melhor indexação
e resultados mais relevantes
"""

import json
import re
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import time
import hashlib
from collections import defaultdict
import math

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SearchType(Enum):
    """Tipos de pesquisa"""
    JURISPRUDENCE = "Jurisprudência"
    LEGISLATION = "Legislação"
    DOCTRINE = "Doutrina"
    CASES = "Casos"
    PRECEDENTS = "Precedentes"
    MIXED = "Mista"

class Court(Enum):
    """Tribunais"""
    STF = "Supremo Tribunal Federal"
    STJ = "Superior Tribunal de Justiça"
    TST = "Tribunal Superior do Trabalho"
    TSE = "Tribunal Superior Eleitoral"
    STM = "Superior Tribunal Militar"
    TJSP = "Tribunal de Justiça de São Paulo"
    TJRJ = "Tribunal de Justiça do Rio de Janeiro"
    TJMG = "Tribunal de Justiça de Minas Gerais"
    TRT = "Tribunal Regional do Trabalho"
    TRF = "Tribunal Regional Federal"

class LegalArea(Enum):
    """Áreas do direito"""
    CIVIL = "Civil"
    PENAL = "Penal"
    TRABALHISTA = "Trabalhista"
    TRIBUTARIO = "Tributário"
    ADMINISTRATIVO = "Administrativo"
    CONSTITUCIONAL = "Constitucional"
    EMPRESARIAL = "Empresarial"
    CONSUMIDOR = "Consumidor"
    FAMILIA = "Família"
    PREVIDENCIARIO = "Previdenciário"

@dataclass
class SearchQuery:
    """Consulta de pesquisa"""
    id: str
    text: str
    search_type: SearchType
    filters: Dict[str, Any]
    user_id: str
    timestamp: datetime

@dataclass
class SearchResult:
    """Resultado de pesquisa"""
    id: str
    title: str
    content: str
    source: str
    court: Optional[Court]
    date: Optional[datetime]
    area: Optional[LegalArea]
    relevance_score: float
    url: Optional[str]
    metadata: Dict[str, Any]

@dataclass
class SearchResponse:
    """Resposta de pesquisa"""
    query_id: str
    results: List[SearchResult]
    total_results: int
    search_time: float
    suggestions: List[str]
    filters_applied: Dict[str, Any]

class LegalDocumentDatabase:
    """Base de dados de documentos jurídicos simulada"""
    
    def __init__(self):
        self.documents = self._load_sample_documents()
        self.index = self._build_index()
    
    def _load_sample_documents(self) -> List[Dict[str, Any]]:
        """Carrega documentos de exemplo"""
        documents = []
        
        # Jurisprudência STJ
        documents.extend([
            {
                "id": "stj_resp_1737428",
                "title": "REsp 1.737.428/RJ - Danos morais por negativação indevida",
                "content": "CIVIL. RESPONSABILIDADE CIVIL. DANOS MORAIS. INSCRIÇÃO INDEVIDA EM ÓRGÃOS DE PROTEÇÃO AO CRÉDITO. DANO MORAL PRESUMIDO. QUANTUM INDENIZATÓRIO. PROPORCIONALIDADE. 1. A inscrição indevida do nome do consumidor em cadastros de proteção ao crédito gera dano moral presumido, dispensando a prova do prejuízo. 2. O valor da indenização deve observar os princípios da proporcionalidade e razoabilidade. 3. Recurso conhecido e provido.",
                "source": "STJ",
                "court": Court.STJ,
                "date": datetime(2023, 5, 15),
                "area": LegalArea.CIVIL,
                "url": "https://stj.jus.br/resp1737428",
                "metadata": {
                    "relator": "Min. Paulo de Tarso Sanseverino",
                    "turma": "3ª Turma",
                    "tipo": "Recurso Especial",
                    "tags": ["danos morais", "negativação", "indenização"]
                }
            },
            {
                "id": "stj_resp_1234567",
                "title": "REsp 1.234.567/SP - Responsabilidade civil do fornecedor",
                "content": "CONSUMIDOR. RESPONSABILIDADE CIVIL. DEFEITO DO PRODUTO. DANOS MATERIAIS E MORAIS. CDC. 1. O fornecedor responde objetivamente pelos danos causados por defeitos de seus produtos. 2. Comprovado o defeito e o nexo causal, devida a reparação integral. 3. Recurso desprovido.",
                "source": "STJ",
                "court": Court.STJ,
                "date": datetime(2023, 8, 22),
                "area": LegalArea.CONSUMIDOR,
                "url": "https://stj.jus.br/resp1234567",
                "metadata": {
                    "relator": "Min. Nancy Andrighi",
                    "turma": "3ª Turma",
                    "tipo": "Recurso Especial",
                    "tags": ["responsabilidade civil", "defeito produto", "cdc"]
                }
            }
        ])
        
        # Jurisprudência STF
        documents.extend([
            {
                "id": "stf_re_123456",
                "title": "RE 123.456 - Direito fundamental à privacidade",
                "content": "CONSTITUCIONAL. DIREITO FUNDAMENTAL À PRIVACIDADE. PROTEÇÃO DE DADOS PESSOAIS. LGPD. 1. A proteção de dados pessoais constitui direito fundamental implícito na Constituição Federal. 2. A LGPD deve ser interpretada em conformidade com os direitos fundamentais. 3. Recurso provido.",
                "source": "STF",
                "court": Court.STF,
                "date": datetime(2024, 1, 10),
                "area": LegalArea.CONSTITUCIONAL,
                "url": "https://stf.jus.br/re123456",
                "metadata": {
                    "relator": "Min. Gilmar Mendes",
                    "turma": "Plenário",
                    "tipo": "Recurso Extraordinário",
                    "tags": ["privacidade", "dados pessoais", "lgpd"]
                }
            }
        ])
        
        # Jurisprudência Trabalhista
        documents.extend([
            {
                "id": "tst_rr_987654",
                "title": "RR 987.654 - Horas extras habituais",
                "content": "TRABALHISTA. HORAS EXTRAS HABITUAIS. INTEGRAÇÃO AO SALÁRIO. 13º SALÁRIO. FÉRIAS. 1. As horas extras prestadas habitualmente integram o salário para todos os efeitos. 2. Devem ser consideradas no cálculo do 13º salário e férias. 3. Recurso conhecido e provido.",
                "source": "TST",
                "court": Court.TST,
                "date": datetime(2023, 11, 5),
                "area": LegalArea.TRABALHISTA,
                "url": "https://tst.jus.br/rr987654",
                "metadata": {
                    "relator": "Min. Mauricio Godinho Delgado",
                    "turma": "3ª Turma",
                    "tipo": "Recurso de Revista",
                    "tags": ["horas extras", "integração salário", "13º salário"]
                }
            }
        ])
        
        # Legislação
        documents.extend([
            {
                "id": "cc_art_186",
                "title": "Código Civil - Art. 186 - Ato Ilícito",
                "content": "Art. 186. Aquele que, por ação ou omissão voluntária, negligência ou imprudência, violar direito e causar dano a outrem, ainda que exclusivamente moral, comete ato ilícito.",
                "source": "Legislação",
                "court": None,
                "date": datetime(2002, 1, 10),
                "area": LegalArea.CIVIL,
                "url": "http://planalto.gov.br/ccivil_03/leis/2002/l10406.htm",
                "metadata": {
                    "lei": "Lei 10.406/2002",
                    "tipo": "Código Civil",
                    "tags": ["ato ilícito", "responsabilidade civil", "dano"]
                }
            },
            {
                "id": "cdc_art_14",
                "title": "CDC - Art. 14 - Responsabilidade do Fornecedor",
                "content": "Art. 14. O fornecedor de serviços responde, independentemente da existência de culpa, pela reparação dos danos causados aos consumidores por defeitos relativos à prestação dos serviços, bem como por informações insuficientes ou inadequadas sobre sua fruição e riscos.",
                "source": "Legislação",
                "court": None,
                "date": datetime(1990, 9, 11),
                "area": LegalArea.CONSUMIDOR,
                "url": "http://planalto.gov.br/ccivil_03/leis/l8078.htm",
                "metadata": {
                    "lei": "Lei 8.078/1990",
                    "tipo": "Código de Defesa do Consumidor",
                    "tags": ["responsabilidade objetiva", "fornecedor", "defeito serviço"]
                }
            }
        ])
        
        # Doutrina
        documents.extend([
            {
                "id": "doutrina_resp_civil",
                "title": "Responsabilidade Civil - Conceitos Fundamentais",
                "content": "A responsabilidade civil constitui instituto fundamental do direito privado, tendo por objetivo a reparação de danos causados a terceiros. Seus elementos essenciais são: conduta (ação ou omissão), dano, nexo causal e, na responsabilidade subjetiva, a culpa. A evolução jurisprudencial tem ampliado as hipóteses de responsabilidade objetiva.",
                "source": "Doutrina",
                "court": None,
                "date": datetime(2023, 1, 1),
                "area": LegalArea.CIVIL,
                "url": None,
                "metadata": {
                    "autor": "Carlos Roberto Gonçalves",
                    "obra": "Direito Civil Brasileiro - Responsabilidade Civil",
                    "tipo": "Livro",
                    "tags": ["responsabilidade civil", "elementos", "dano"]
                }
            }
        ])
        
        return documents
    
    def _build_index(self) -> Dict[str, List[str]]:
        """Constrói índice invertido para busca"""
        index = defaultdict(list)
        
        for doc in self.documents:
            # Indexa título e conteúdo
            text = f"{doc['title']} {doc['content']}".lower()
            
            # Remove pontuação e divide em palavras
            words = re.findall(r'\b\w+\b', text)
            
            # Remove palavras muito comuns (stop words)
            stop_words = {
                'a', 'o', 'e', 'de', 'do', 'da', 'em', 'um', 'uma', 'para', 'com', 'por',
                'que', 'se', 'na', 'no', 'ao', 'aos', 'das', 'dos', 'pela', 'pelo'
            }
            
            for word in words:
                if len(word) > 2 and word not in stop_words:
                    index[word].append(doc['id'])
        
        return dict(index)
    
    def search(self, query: str, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Busca documentos"""
        if filters is None:
            filters = {}
        
        # Processa query
        query_words = re.findall(r'\b\w+\b', query.lower())
        query_words = [w for w in query_words if len(w) > 2]
        
        if not query_words:
            return []
        
        # Busca documentos que contêm as palavras
        doc_scores = defaultdict(float)
        
        for word in query_words:
            if word in self.index:
                for doc_id in self.index[word]:
                    doc_scores[doc_id] += 1.0 / len(self.index[word])  # TF-IDF simplificado
        
        # Aplica filtros
        filtered_docs = []
        for doc in self.documents:
            if doc['id'] in doc_scores:
                # Filtro por tribunal
                if 'court' in filters and filters['court']:
                    if doc['court'] != filters['court']:
                        continue
                
                # Filtro por área
                if 'area' in filters and filters['area']:
                    if doc['area'] != filters['area']:
                        continue
                
                # Filtro por data
                if 'date_from' in filters and filters['date_from']:
                    if doc['date'] and doc['date'] < filters['date_from']:
                        continue
                
                if 'date_to' in filters and filters['date_to']:
                    if doc['date'] and doc['date'] > filters['date_to']:
                        continue
                
                doc_copy = doc.copy()
                doc_copy['relevance_score'] = doc_scores[doc['id']]
                filtered_docs.append(doc_copy)
        
        # Ordena por relevância
        filtered_docs.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return filtered_docs

class EnhancedSearchEngine:
    """Motor de busca aprimorado"""
    
    def __init__(self):
        self.database = LegalDocumentDatabase()
        self.search_history = {}
        self.query_suggestions = self._load_query_suggestions()
    
    def _load_query_suggestions(self) -> Dict[str, List[str]]:
        """Carrega sugestões de consulta"""
        return {
            "danos morais": [
                "danos morais negativação indevida",
                "danos morais valor indenização",
                "danos morais pessoa jurídica",
                "danos morais acidente trânsito"
            ],
            "responsabilidade civil": [
                "responsabilidade civil objetiva",
                "responsabilidade civil médica",
                "responsabilidade civil estado",
                "responsabilidade civil dano moral"
            ],
            "horas extras": [
                "horas extras cálculo",
                "horas extras habitualidade",
                "horas extras adicional noturno",
                "horas extras integração salário"
            ],
            "consumidor": [
                "direitos básicos consumidor",
                "defeito produto consumidor",
                "publicidade enganosa",
                "inversão ônus prova"
            ]
        }
    
    def search(self, query: SearchQuery) -> SearchResponse:
        """Executa pesquisa"""
        start_time = time.time()
        
        logger.info(f"Executando pesquisa: {query.text}")
        
        # Expande query com sinônimos e termos relacionados
        expanded_query = self._expand_query(query.text)
        
        # Busca na base de dados
        raw_results = self.database.search(expanded_query, query.filters)
        
        # Converte para objetos SearchResult
        results = []
        for doc in raw_results:
            result = SearchResult(
                id=doc['id'],
                title=doc['title'],
                content=doc['content'],
                source=doc['source'],
                court=doc.get('court'),
                date=doc.get('date'),
                area=doc.get('area'),
                relevance_score=doc.get('relevance_score', 0.0),
                url=doc.get('url'),
                metadata=doc.get('metadata', {})
            )
            results.append(result)
        
        # Gera sugestões
        suggestions = self._generate_suggestions(query.text)
        
        search_time = time.time() - start_time
        
        # Cria resposta
        response = SearchResponse(
            query_id=query.id,
            results=results,
            total_results=len(results),
            search_time=search_time,
            suggestions=suggestions,
            filters_applied=query.filters
        )
        
        # Armazena no histórico
        self._store_search_history(query, response)
        
        logger.info(f"Pesquisa concluída: {len(results)} resultados em {search_time:.3f}s")
        
        return response
    
    def _expand_query(self, query: str) -> str:
        """Expande query com sinônimos e termos relacionados"""
        # Dicionário de sinônimos simplificado
        synonyms = {
            "dano": ["prejuízo", "lesão"],
            "indenização": ["reparação", "compensação"],
            "responsabilidade": ["obrigação", "dever"],
            "contrato": ["acordo", "pacto"],
            "consumidor": ["cliente", "adquirente"],
            "fornecedor": ["prestador", "vendedor"]
        }
        
        expanded_terms = [query]
        query_words = query.lower().split()
        
        for word in query_words:
            if word in synonyms:
                for synonym in synonyms[word]:
                    expanded_terms.append(f"{query} {synonym}")
        
        return " ".join(expanded_terms)
    
    def _generate_suggestions(self, query: str) -> List[str]:
        """Gera sugestões de pesquisa"""
        suggestions = []
        query_lower = query.lower()
        
        # Busca sugestões baseadas em palavras-chave
        for key, suggestion_list in self.query_suggestions.items():
            if key in query_lower:
                suggestions.extend(suggestion_list)
        
        # Sugestões genéricas baseadas no tipo de consulta
        if "danos" in query_lower:
            suggestions.extend([
                "danos morais valor",
                "danos materiais cálculo",
                "danos estéticos"
            ])
        
        if "contrato" in query_lower:
            suggestions.extend([
                "rescisão contratual",
                "cláusulas abusivas",
                "inadimplemento contratual"
            ])
        
        # Remove duplicatas e limita a 5 sugestões
        suggestions = list(set(suggestions))
        return suggestions[:5]
    
    def _store_search_history(self, query: SearchQuery, response: SearchResponse):
        """Armazena histórico de pesquisa"""
        if query.user_id not in self.search_history:
            self.search_history[query.user_id] = []
        
        self.search_history[query.user_id].append({
            "query": query.text,
            "search_type": query.search_type.value,
            "results_count": response.total_results,
            "search_time": response.search_time,
            "timestamp": query.timestamp.isoformat()
        })
        
        # Mantém apenas últimas 50 pesquisas por usuário
        if len(self.search_history[query.user_id]) > 50:
            self.search_history[query.user_id] = self.search_history[query.user_id][-50:]
    
    def get_search_analytics(self, user_id: str = None) -> Dict[str, Any]:
        """Retorna analytics de pesquisa"""
        if user_id and user_id in self.search_history:
            history = self.search_history[user_id]
        else:
            # Combina histórico de todos os usuários
            history = []
            for user_history in self.search_history.values():
                history.extend(user_history)
        
        if not history:
            return {"message": "Nenhuma pesquisa realizada"}
        
        # Estatísticas básicas
        total_searches = len(history)
        avg_results = sum(h['results_count'] for h in history) / total_searches
        avg_search_time = sum(h['search_time'] for h in history) / total_searches
        
        # Tipos de pesquisa mais comuns
        search_types = defaultdict(int)
        for h in history:
            search_types[h['search_type']] += 1
        
        # Termos mais pesquisados
        query_terms = defaultdict(int)
        for h in history:
            words = h['query'].lower().split()
            for word in words:
                if len(word) > 3:  # Ignora palavras muito curtas
                    query_terms[word] += 1
        
        top_terms = sorted(query_terms.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "total_searches": total_searches,
            "average_results_per_search": round(avg_results, 1),
            "average_search_time": round(avg_search_time, 3),
            "search_types": dict(search_types),
            "top_search_terms": dict(top_terms),
            "recent_searches": [h['query'] for h in history[-5:]]
        }
    
    def advanced_search(self, query_text: str, filters: Dict[str, Any], 
                       user_id: str = "default") -> SearchResponse:
        """Pesquisa avançada com filtros"""
        query = SearchQuery(
            id=f"search_{int(time.time())}_{user_id}",
            text=query_text,
            search_type=SearchType.MIXED,
            filters=filters,
            user_id=user_id,
            timestamp=datetime.now()
        )
        
        return self.search(query)
    
    def semantic_search(self, query_text: str, user_id: str = "default") -> SearchResponse:
        """Pesquisa semântica (simulada)"""
        # Simula pesquisa semântica expandindo a query com conceitos relacionados
        semantic_expansions = {
            "responsabilidade civil": "ato ilícito dano nexo causal culpa indenização reparação",
            "danos morais": "sofrimento angústia humilhação constrangimento dignidade honra imagem",
            "consumidor": "relação consumo fornecedor produto serviço defeito vício",
            "contrato": "obrigação prestação inadimplemento rescisão cláusula acordo"
        }
        
        expanded_query = query_text
        for concept, expansion in semantic_expansions.items():
            if concept in query_text.lower():
                expanded_query += f" {expansion}"
        
        query = SearchQuery(
            id=f"semantic_{int(time.time())}_{user_id}",
            text=expanded_query,
            search_type=SearchType.MIXED,
            filters={},
            user_id=user_id,
            timestamp=datetime.now()
        )
        
        return self.search(query)
    
    def get_related_documents(self, document_id: str) -> List[SearchResult]:
        """Retorna documentos relacionados"""
        # Encontra documento base
        base_doc = None
        for doc in self.database.documents:
            if doc['id'] == document_id:
                base_doc = doc
                break
        
        if not base_doc:
            return []
        
        # Busca documentos da mesma área
        related = []
        for doc in self.database.documents:
            if (doc['id'] != document_id and 
                doc['area'] == base_doc['area'] and
                len(related) < 5):
                
                result = SearchResult(
                    id=doc['id'],
                    title=doc['title'],
                    content=doc['content'][:200] + "...",
                    source=doc['source'],
                    court=doc.get('court'),
                    date=doc.get('date'),
                    area=doc.get('area'),
                    relevance_score=0.8,  # Score fixo para relacionados
                    url=doc.get('url'),
                    metadata=doc.get('metadata', {})
                )
                related.append(result)
        
        return related

def main():
    """Função principal para demonstração"""
    print("=== Pesquisa Jurídica Inteligente - Versão Melhorada ===")
    
    # Cria instância do motor de busca
    search_engine = EnhancedSearchEngine()
    
    # Consultas de exemplo
    consultas_exemplo = [
        "danos morais por negativação indevida",
        "responsabilidade civil do fornecedor",
        "horas extras habituais integração salário",
        "direito fundamental privacidade dados pessoais"
    ]
    
    print(f"\nExecutando {len(consultas_exemplo)} pesquisas de exemplo...")
    
    for i, consulta in enumerate(consultas_exemplo, 1):
        print(f"\n--- Pesquisa {i} ---")
        print(f"Consulta: {consulta}")
        
        # Pesquisa simples
        response = search_engine.advanced_search(consulta, {}, "usuario_teste")
        
        print(f"Resultados encontrados: {response.total_results}")
        print(f"Tempo de pesquisa: {response.search_time:.3f}s")
        
        # Mostra primeiros resultados
        for j, result in enumerate(response.results[:2], 1):
            print(f"\n{j}. {result.title}")
            print(f"   Fonte: {result.source}")
            print(f"   Relevância: {result.relevance_score:.2f}")
            print(f"   Resumo: {result.content[:150]}...")
        
        # Mostra sugestões
        if response.suggestions:
            print(f"\nSugestões: {', '.join(response.suggestions[:3])}")
    
    # Pesquisa avançada com filtros
    print(f"\n--- Pesquisa Avançada ---")
    filtros = {
        "court": Court.STJ,
        "area": LegalArea.CIVIL,
        "date_from": datetime(2023, 1, 1)
    }
    
    response_avancada = search_engine.advanced_search(
        "responsabilidade civil", filtros, "usuario_teste"
    )
    
    print(f"Pesquisa com filtros (STJ, Civil, 2023+): {response_avancada.total_results} resultados")
    
    # Pesquisa semântica
    print(f"\n--- Pesquisa Semântica ---")
    response_semantica = search_engine.semantic_search(
        "responsabilidade civil", "usuario_teste"
    )
    
    print(f"Pesquisa semântica: {response_semantica.total_results} resultados")
    
    # Documentos relacionados
    print(f"\n--- Documentos Relacionados ---")
    if response.results:
        relacionados = search_engine.get_related_documents(response.results[0].id)
        print(f"Documentos relacionados a '{response.results[0].title}': {len(relacionados)}")
        
        for rel in relacionados[:2]:
            print(f"- {rel.title}")
    
    # Analytics
    analytics = search_engine.get_search_analytics("usuario_teste")
    print(f"\n--- Analytics ---")
    print(f"Total de pesquisas: {analytics['total_searches']}")
    print(f"Média de resultados: {analytics['average_results_per_search']}")
    print(f"Tempo médio: {analytics['average_search_time']}s")
    print(f"Termos mais pesquisados: {list(analytics['top_search_terms'].keys())[:3]}")
    
    return search_engine

if __name__ == "__main__":
    main()

