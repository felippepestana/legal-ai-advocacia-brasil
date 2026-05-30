#!/usr/bin/env python3
"""
Análise Inteligente de Documentos - Versão Melhorada
Implementa melhorias: algoritmos refinados, melhor reconhecimento de documentos complexos
e performance otimizada
"""

import json
import re
import os
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import time
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentType(Enum):
    """Tipos de documentos jurídicos"""
    PETICAO_INICIAL = "Petição Inicial"
    CONTESTACAO = "Contestação"
    SENTENCA = "Sentença"
    ACORDAO = "Acórdão"
    DESPACHO = "Despacho"
    DECISAO_INTERLOCUTORIA = "Decisão Interlocutória"
    CONTRATO = "Contrato"
    PROCURACAO = "Procuração"
    ATA_AUDIENCIA = "Ata de Audiência"
    LAUDO_PERICIAL = "Laudo Pericial"
    PARECER = "Parecer"
    RECURSO = "Recurso"
    EMBARGOS = "Embargos"
    MANDADO = "Mandado"
    CERTIDAO = "Certidão"
    OUTROS = "Outros"

class EntityType(Enum):
    """Tipos de entidades jurídicas"""
    PESSOA_FISICA = "Pessoa Física"
    PESSOA_JURIDICA = "Pessoa Jurídica"
    ADVOGADO = "Advogado"
    JUIZ = "Juiz"
    PROMOTOR = "Promotor"
    PROCESSO = "Número de Processo"
    CPF = "CPF"
    CNPJ = "CNPJ"
    OAB = "OAB"
    VALOR_MONETARIO = "Valor Monetário"
    DATA = "Data"
    ENDERECO = "Endereço"
    TELEFONE = "Telefone"
    EMAIL = "Email"
    TRIBUNAL = "Tribunal"
    VARA = "Vara"
    COMARCA = "Comarca"

@dataclass
class Entity:
    """Entidade extraída do documento"""
    text: str
    type: EntityType
    confidence: float
    start_pos: int
    end_pos: int
    context: str = ""
    normalized_value: str = ""

@dataclass
class LegalConcept:
    """Conceito jurídico identificado"""
    concept: str
    category: str
    confidence: float
    context: str
    related_articles: List[str] = None
    
    def __post_init__(self):
        if self.related_articles is None:
            self.related_articles = []

@dataclass
class DocumentAnalysis:
    """Resultado da análise de documento"""
    document_id: str
    document_type: DocumentType
    confidence: float
    entities: List[Entity]
    legal_concepts: List[LegalConcept]
    summary: str
    key_points: List[str]
    processing_time: float
    metadata: Dict[str, Any]

class EnhancedEntityExtractor:
    """Extrator aprimorado de entidades com algoritmos refinados"""
    
    def __init__(self):
        self.patterns = {
            EntityType.PROCESSO: [
                r'\b\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}\b',  # Padrão CNJ
                r'\b\d{4}\.\d{3}\.\d{3}-\d\b',  # Padrão antigo
                r'\b\d{6}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}\b'   # Variação
            ],
            EntityType.CPF: [
                r'\b\d{3}\.\d{3}\.\d{3}-\d{2}\b',
                r'\bCPF:?\s*\d{3}\.\d{3}\.\d{3}-\d{2}\b',
                r'\b\d{11}\b(?=.*cpf|CPF)'
            ],
            EntityType.CNPJ: [
                r'\b\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\b',
                r'\bCNPJ:?\s*\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\b',
                r'\b\d{14}\b(?=.*cnpj|CNPJ)'
            ],
            EntityType.OAB: [
                r'\bOAB[/-]?[A-Z]{2}\s*\d+\b',
                r'\bOAB\s*nº?\s*\d+[/-]?[A-Z]{2}\b'
            ],
            EntityType.VALOR_MONETARIO: [
                r'R\$\s*\d{1,3}(?:\.\d{3})*(?:,\d{2})?',
                r'\b\d{1,3}(?:\.\d{3})*(?:,\d{2})?\s*reais?\b',
                r'valor.*?R\$\s*\d{1,3}(?:\.\d{3})*(?:,\d{2})?'
            ],
            EntityType.DATA: [
                r'\b\d{1,2}[/-]\d{1,2}[/-]\d{4}\b',
                r'\b\d{1,2}\s+de\s+\w+\s+de\s+\d{4}\b',
                r'\b\w+,\s*\d{1,2}\s+de\s+\w+\s+de\s+\d{4}\b'
            ],
            EntityType.EMAIL: [
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            ],
            EntityType.TELEFONE: [
                r'\(\d{2}\)\s*\d{4,5}-?\d{4}',
                r'\b\d{2}\s*\d{4,5}-?\d{4}\b',
                r'\+55\s*\d{2}\s*\d{4,5}-?\d{4}'
            ]
        }
        
        self.name_patterns = {
            EntityType.PESSOA_FISICA: [
                r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b',
                r'(?:Sr\.|Sra\.|Dr\.|Dra\.)\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+',
                r'requer(?:ente|ido):\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)'
            ],
            EntityType.ADVOGADO: [
                r'(?:Dr\.|Dra\.)\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+(?:\s*-\s*OAB)',
                r'Advogado[a]?:\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
                r'subscrito.*?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+).*?OAB'
            ],
            EntityType.JUIZ: [
                r'(?:Juiz|Juíza|Desembargador|Desembargadora)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
                r'MM\.?\s*(?:Juiz|Juíza)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)'
            ]
        }
    
    def extract_entities(self, text: str) -> List[Entity]:
        """Extrai entidades do texto com algoritmos refinados"""
        entities = []
        
        # Extrai entidades por padrões regex
        for entity_type, patterns in self.patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    entity = Entity(
                        text=match.group(0),
                        type=entity_type,
                        confidence=self._calculate_confidence(match.group(0), entity_type),
                        start_pos=match.start(),
                        end_pos=match.end(),
                        context=self._extract_context(text, match.start(), match.end()),
                        normalized_value=self._normalize_value(match.group(0), entity_type)
                    )
                    entities.append(entity)
        
        # Extrai nomes e pessoas
        for entity_type, patterns in self.name_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    name = match.group(1) if match.groups() else match.group(0)
                    entity = Entity(
                        text=name.strip(),
                        type=entity_type,
                        confidence=self._calculate_name_confidence(name, entity_type),
                        start_pos=match.start(),
                        end_pos=match.end(),
                        context=self._extract_context(text, match.start(), match.end()),
                        normalized_value=self._normalize_name(name)
                    )
                    entities.append(entity)
        
        # Remove duplicatas e entidades de baixa confiança
        entities = self._filter_entities(entities)
        
        return entities
    
    def _calculate_confidence(self, text: str, entity_type: EntityType) -> float:
        """Calcula confiança da extração baseada em validações"""
        base_confidence = 0.8
        
        if entity_type == EntityType.CPF:
            return base_confidence + (0.2 if self._validate_cpf(text) else -0.3)
        elif entity_type == EntityType.CNPJ:
            return base_confidence + (0.2 if self._validate_cnpj(text) else -0.3)
        elif entity_type == EntityType.PROCESSO:
            return base_confidence + (0.15 if len(text) >= 15 else -0.2)
        elif entity_type == EntityType.EMAIL:
            return base_confidence + (0.1 if '@' in text and '.' in text else -0.4)
        
        return base_confidence
    
    def _calculate_name_confidence(self, name: str, entity_type: EntityType) -> float:
        """Calcula confiança para nomes baseado em heurísticas"""
        base_confidence = 0.7
        
        # Verifica se tem pelo menos 2 palavras
        words = name.split()
        if len(words) < 2:
            return base_confidence - 0.3
        
        # Verifica se todas as palavras começam com maiúscula
        if all(word[0].isupper() for word in words if word):
            base_confidence += 0.2
        
        # Verifica se não contém números
        if not any(char.isdigit() for char in name):
            base_confidence += 0.1
        
        return min(base_confidence, 0.95)
    
    def _validate_cpf(self, cpf: str) -> bool:
        """Valida CPF usando algoritmo de dígito verificador"""
        cpf = re.sub(r'[^0-9]', '', cpf)
        if len(cpf) != 11 or cpf == cpf[0] * 11:
            return False
        
        # Calcula primeiro dígito
        sum1 = sum(int(cpf[i]) * (10 - i) for i in range(9))
        digit1 = 11 - (sum1 % 11)
        if digit1 >= 10:
            digit1 = 0
        
        # Calcula segundo dígito
        sum2 = sum(int(cpf[i]) * (11 - i) for i in range(10))
        digit2 = 11 - (sum2 % 11)
        if digit2 >= 10:
            digit2 = 0
        
        return cpf[-2:] == f"{digit1}{digit2}"
    
    def _validate_cnpj(self, cnpj: str) -> bool:
        """Valida CNPJ usando algoritmo de dígito verificador"""
        cnpj = re.sub(r'[^0-9]', '', cnpj)
        if len(cnpj) != 14:
            return False
        
        # Algoritmo de validação do CNPJ
        weights1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        weights2 = [6, 7, 8, 9, 2, 3, 4, 5, 6, 7, 8, 9]
        
        sum1 = sum(int(cnpj[i]) * weights1[i] for i in range(12))
        digit1 = 11 - (sum1 % 11)
        if digit1 >= 10:
            digit1 = 0
        
        weights2_full = [6, 7, 8, 9, 2, 3, 4, 5, 6, 7, 8, 9, 2]
        sum2 = sum(int(cnpj[i]) * weights2_full[i] for i in range(13))
        digit2 = 11 - (sum2 % 11)
        if digit2 >= 10:
            digit2 = 0
        
        return cnpj[-2:] == f"{digit1}{digit2}"
    
    def _extract_context(self, text: str, start: int, end: int, window: int = 50) -> str:
        """Extrai contexto ao redor da entidade"""
        context_start = max(0, start - window)
        context_end = min(len(text), end + window)
        return text[context_start:context_end].strip()
    
    def _normalize_value(self, value: str, entity_type: EntityType) -> str:
        """Normaliza valores extraídos"""
        if entity_type == EntityType.CPF:
            return re.sub(r'[^0-9]', '', value)
        elif entity_type == EntityType.CNPJ:
            return re.sub(r'[^0-9]', '', value)
        elif entity_type == EntityType.VALOR_MONETARIO:
            # Remove R$ e converte para float
            value = re.sub(r'[R$\s]', '', value)
            value = value.replace('.', '').replace(',', '.')
            try:
                return str(float(value))
            except:
                return value
        
        return value.strip()
    
    def _normalize_name(self, name: str) -> str:
        """Normaliza nomes próprios"""
        return ' '.join(word.capitalize() for word in name.split())
    
    def _filter_entities(self, entities: List[Entity]) -> List[Entity]:
        """Remove duplicatas e entidades de baixa confiança"""
        # Remove entidades com confiança muito baixa
        filtered = [e for e in entities if e.confidence >= 0.5]
        
        # Remove duplicatas baseado em texto e tipo
        seen = set()
        unique_entities = []
        
        for entity in filtered:
            key = (entity.text.lower(), entity.type)
            if key not in seen:
                seen.add(key)
                unique_entities.append(entity)
        
        return unique_entities

class EnhancedConceptExtractor:
    """Extrator aprimorado de conceitos jurídicos"""
    
    def __init__(self):
        self.legal_concepts = {
            "Direito Civil": [
                "danos morais", "danos materiais", "responsabilidade civil",
                "contrato", "obrigação", "inadimplemento", "rescisão",
                "indenização", "lucros cessantes", "dano emergente"
            ],
            "Direito do Consumidor": [
                "código de defesa do consumidor", "cdc", "relação de consumo",
                "vício do produto", "defeito do produto", "publicidade enganosa",
                "práticas abusivas", "inversão do ônus da prova"
            ],
            "Direito Trabalhista": [
                "clt", "consolidação das leis do trabalho", "jornada de trabalho",
                "horas extras", "adicional noturno", "fgts", "aviso prévio",
                "rescisão do contrato", "verbas rescisórias"
            ],
            "Direito Penal": [
                "crime", "contravenção", "dolo", "culpa", "legítima defesa",
                "estado de necessidade", "prescrição", "decadência"
            ],
            "Direito Processual": [
                "petição inicial", "contestação", "tríplica", "sentença",
                "recurso", "apelação", "embargos", "execução"
            ]
        }
        
        self.legal_articles = {
            "art. 927": "Responsabilidade Civil",
            "art. 186": "Ato Ilícito",
            "art. 389": "Inadimplemento",
            "art. 6º cdc": "Direitos Básicos do Consumidor",
            "art. 14 cdc": "Responsabilidade do Fornecedor"
        }
    
    def extract_concepts(self, text: str) -> List[LegalConcept]:
        """Extrai conceitos jurídicos do texto"""
        concepts = []
        text_lower = text.lower()
        
        for category, concept_list in self.legal_concepts.items():
            for concept in concept_list:
                if concept.lower() in text_lower:
                    # Encontra todas as ocorrências
                    pattern = re.escape(concept.lower())
                    matches = list(re.finditer(pattern, text_lower))
                    
                    for match in matches:
                        context = self._extract_concept_context(text, match.start(), match.end())
                        confidence = self._calculate_concept_confidence(concept, context)
                        
                        legal_concept = LegalConcept(
                            concept=concept,
                            category=category,
                            confidence=confidence,
                            context=context,
                            related_articles=self._find_related_articles(concept)
                        )
                        concepts.append(legal_concept)
        
        # Remove duplicatas
        unique_concepts = []
        seen = set()
        
        for concept in concepts:
            key = (concept.concept.lower(), concept.category)
            if key not in seen:
                seen.add(key)
                unique_concepts.append(concept)
        
        return unique_concepts
    
    def _extract_concept_context(self, text: str, start: int, end: int, window: int = 100) -> str:
        """Extrai contexto ao redor do conceito"""
        context_start = max(0, start - window)
        context_end = min(len(text), end + window)
        return text[context_start:context_end].strip()
    
    def _calculate_concept_confidence(self, concept: str, context: str) -> float:
        """Calcula confiança do conceito baseado no contexto"""
        base_confidence = 0.8
        
        # Verifica se está em contexto jurídico
        legal_indicators = ["artigo", "lei", "código", "jurisprudência", "tribunal"]
        if any(indicator in context.lower() for indicator in legal_indicators):
            base_confidence += 0.15
        
        # Verifica se está próximo de citações legais
        if re.search(r'art\.?\s*\d+', context.lower()):
            base_confidence += 0.1
        
        return min(base_confidence, 0.95)
    
    def _find_related_articles(self, concept: str) -> List[str]:
        """Encontra artigos relacionados ao conceito"""
        related = []
        concept_lower = concept.lower()
        
        for article, description in self.legal_articles.items():
            if concept_lower in description.lower():
                related.append(article)
        
        return related

class EnhancedDocumentClassifier:
    """Classificador aprimorado de tipos de documento"""
    
    def __init__(self):
        self.document_indicators = {
            DocumentType.PETICAO_INICIAL: [
                "petição inicial", "excelentíssimo", "requer", "pelos fatos e fundamentos",
                "termos em que pede deferimento"
            ],
            DocumentType.CONTESTACAO: [
                "contestação", "impugna", "preliminarmente", "no mérito",
                "requer a improcedência"
            ],
            DocumentType.SENTENCA: [
                "sentença", "julgo procedente", "julgo improcedente", "dispositivo",
                "isto posto", "ante o exposto"
            ],
            DocumentType.ACORDAO: [
                "acórdão", "tribunal", "relator", "ementa", "vistos e relatados",
                "acordam os desembargadores"
            ],
            DocumentType.DESPACHO: [
                "despacho", "intime-se", "cite-se", "cumpra-se", "arquive-se"
            ],
            DocumentType.CONTRATO: [
                "contrato", "contratante", "contratado", "cláusula", "partes",
                "objeto do contrato"
            ],
            DocumentType.PROCURACAO: [
                "procuração", "outorgante", "outorgado", "poderes", "substabelecer"
            ]
        }
    
    def classify_document(self, text: str) -> Tuple[DocumentType, float]:
        """Classifica o tipo de documento"""
        text_lower = text.lower()
        scores = {}
        
        for doc_type, indicators in self.document_indicators.items():
            score = 0
            total_indicators = len(indicators)
            
            for indicator in indicators:
                if indicator in text_lower:
                    # Pontuação baseada na frequência e posição
                    occurrences = text_lower.count(indicator)
                    position_bonus = 1.5 if text_lower.find(indicator) < len(text_lower) * 0.3 else 1.0
                    score += occurrences * position_bonus
            
            # Normaliza a pontuação
            normalized_score = min(score / total_indicators, 1.0)
            scores[doc_type] = normalized_score
        
        # Retorna o tipo com maior pontuação
        best_type = max(scores, key=scores.get)
        confidence = scores[best_type]
        
        # Se a confiança for muito baixa, classifica como "Outros"
        if confidence < 0.3:
            return DocumentType.OUTROS, confidence
        
        return best_type, confidence

class EnhancedDocumentAnalyzer:
    """Analisador aprimorado de documentos com todas as melhorias"""
    
    def __init__(self):
        self.entity_extractor = EnhancedEntityExtractor()
        self.concept_extractor = EnhancedConceptExtractor()
        self.classifier = EnhancedDocumentClassifier()
        self.cache = {}  # Cache para otimização de performance
    
    def analyze_document(self, text: str, document_id: str = None) -> DocumentAnalysis:
        """Analisa documento completo com performance otimizada"""
        start_time = time.time()
        
        if document_id is None:
            document_id = hashlib.md5(text.encode()).hexdigest()[:12]
        
        # Verifica cache
        if document_id in self.cache:
            logger.info(f"Retornando análise do cache para documento {document_id}")
            return self.cache[document_id]
        
        logger.info(f"Iniciando análise do documento {document_id}")
        
        # Análise paralela para melhor performance
        with ThreadPoolExecutor(max_workers=3) as executor:
            # Submete tarefas em paralelo
            entity_future = executor.submit(self.entity_extractor.extract_entities, text)
            concept_future = executor.submit(self.concept_extractor.extract_concepts, text)
            classification_future = executor.submit(self.classifier.classify_document, text)
            
            # Coleta resultados
            entities = entity_future.result()
            concepts = concept_future.result()
            doc_type, type_confidence = classification_future.result()
        
        # Gera resumo e pontos-chave
        summary = self._generate_summary(text, entities, concepts)
        key_points = self._extract_key_points(text, entities, concepts)
        
        processing_time = time.time() - start_time
        
        # Cria resultado da análise
        analysis = DocumentAnalysis(
            document_id=document_id,
            document_type=doc_type,
            confidence=type_confidence,
            entities=entities,
            legal_concepts=concepts,
            summary=summary,
            key_points=key_points,
            processing_time=processing_time,
            metadata={
                "text_length": len(text),
                "entities_count": len(entities),
                "concepts_count": len(concepts),
                "analysis_timestamp": datetime.now().isoformat()
            }
        )
        
        # Armazena no cache
        self.cache[document_id] = analysis
        
        logger.info(f"Análise concluída em {processing_time:.2f}s")
        return analysis
    
    def _generate_summary(self, text: str, entities: List[Entity], concepts: List[LegalConcept]) -> str:
        """Gera resumo inteligente do documento"""
        # Identifica partes principais
        partes = [e.text for e in entities if e.type in [EntityType.PESSOA_FISICA, EntityType.PESSOA_JURIDICA]]
        processos = [e.text for e in entities if e.type == EntityType.PROCESSO]
        valores = [e.text for e in entities if e.type == EntityType.VALOR_MONETARIO]
        
        summary_parts = []
        
        if partes:
            summary_parts.append(f"Partes envolvidas: {', '.join(partes[:3])}")
        
        if processos:
            summary_parts.append(f"Processo: {processos[0]}")
        
        if valores:
            summary_parts.append(f"Valores mencionados: {', '.join(valores[:2])}")
        
        if concepts:
            main_concepts = [c.concept for c in concepts[:3]]
            summary_parts.append(f"Conceitos principais: {', '.join(main_concepts)}")
        
        return ". ".join(summary_parts) if summary_parts else "Documento analisado sem informações específicas identificadas."
    
    def _extract_key_points(self, text: str, entities: List[Entity], concepts: List[LegalConcept]) -> List[str]:
        """Extrai pontos-chave do documento"""
        key_points = []
        
        # Pontos baseados em entidades importantes
        high_value_entities = [e for e in entities if e.confidence >= 0.8]
        for entity in high_value_entities[:5]:
            key_points.append(f"{entity.type.value}: {entity.text}")
        
        # Pontos baseados em conceitos jurídicos
        important_concepts = [c for c in concepts if c.confidence >= 0.8]
        for concept in important_concepts[:3]:
            key_points.append(f"Conceito jurídico: {concept.concept} ({concept.category})")
        
        # Busca por frases importantes
        important_phrases = self._find_important_phrases(text)
        key_points.extend(important_phrases[:3])
        
        return key_points
    
    def _find_important_phrases(self, text: str) -> List[str]:
        """Encontra frases importantes no texto"""
        important_patterns = [
            r'[Rr]equer.*?[\.;]',
            r'[Jj]ulgo.*?[\.;]',
            r'[Cc]ondeno.*?[\.;]',
            r'[Dd]efiro.*?[\.;]',
            r'[Ii]ndefiro.*?[\.;]'
        ]
        
        phrases = []
        for pattern in important_patterns:
            matches = re.findall(pattern, text)
            phrases.extend(matches[:2])  # Máximo 2 por padrão
        
        return [phrase.strip() for phrase in phrases]
    
    def get_analysis_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas das análises realizadas"""
        if not self.cache:
            return {"message": "Nenhuma análise realizada ainda"}
        
        analyses = list(self.cache.values())
        
        return {
            "total_analyses": len(analyses),
            "average_processing_time": sum(a.processing_time for a in analyses) / len(analyses),
            "document_types": {dt.value: sum(1 for a in analyses if a.document_type == dt) 
                             for dt in DocumentType},
            "average_entities_per_doc": sum(len(a.entities) for a in analyses) / len(analyses),
            "average_concepts_per_doc": sum(len(a.legal_concepts) for a in analyses) / len(analyses)
        }

def main():
    """Função principal para demonstração"""
    print("=== Análise Inteligente de Documentos - Versão Melhorada ===")
    
    # Cria instância do analisador
    analyzer = EnhancedDocumentAnalyzer()
    
    # Documento de exemplo
    documento_exemplo = """
    EXCELENTÍSSIMO SENHOR DOUTOR JUIZ DE DIREITO DA 1ª VARA CÍVEL DA COMARCA DE SÃO PAULO
    
    JOÃO SILVA, brasileiro, casado, empresário, portador do CPF nº 123.456.789-10,
    residente e domiciliado na Rua das Flores, 123, São Paulo/SP, por seu advogado
    Dr. Carlos Santos, OAB/SP 123456, vem respeitosamente à presença de Vossa Excelência
    propor a presente
    
    AÇÃO DE INDENIZAÇÃO POR DANOS MORAIS E MATERIAIS
    
    em face de BANCO XYZ S.A., pessoa jurídica de direito privado, CNPJ 12.345.678/0001-90,
    com sede na Av. Paulista, 1000, São Paulo/SP, pelos fatos e fundamentos a seguir expostos:
    
    DOS FATOS
    
    O requerente mantinha conta corrente junto ao requerido, quando teve seu nome
    indevidamente inscrito nos órgãos de proteção ao crédito no valor de R$ 5.000,00,
    causando-lhe danos morais e materiais.
    
    DO DIREITO
    
    A conduta do requerido configura danos morais, conforme art. 186 do Código Civil
    e art. 6º do CDC, sendo devida indenização.
    
    DOS PEDIDOS
    
    Ante o exposto, requer:
    a) A condenação do réu ao pagamento de indenização por danos morais no valor de R$ 20.000,00;
    b) A condenação do réu ao pagamento de danos materiais no valor de R$ 2.000,00;
    
    Termos em que pede deferimento.
    
    São Paulo, 12 de setembro de 2024.
    
    Dr. Carlos Santos
    OAB/SP 123456
    """
    
    # Analisa documento
    analysis = analyzer.analyze_document(documento_exemplo)
    
    # Exibe resultados
    print(f"\nTipo de Documento: {analysis.document_type.value} (Confiança: {analysis.confidence:.2f})")
    print(f"Tempo de Processamento: {analysis.processing_time:.3f}s")
    
    print(f"\nEntidades Extraídas ({len(analysis.entities)}):")
    for entity in analysis.entities[:10]:  # Mostra apenas as primeiras 10
        print(f"- {entity.type.value}: {entity.text} (Confiança: {entity.confidence:.2f})")
    
    print(f"\nConceitos Jurídicos ({len(analysis.legal_concepts)}):")
    for concept in analysis.legal_concepts:
        print(f"- {concept.concept} ({concept.category}) - Confiança: {concept.confidence:.2f}")
    
    print(f"\nResumo:")
    print(analysis.summary)
    
    print(f"\nPontos-Chave:")
    for point in analysis.key_points:
        print(f"- {point}")
    
    # Estatísticas
    stats = analyzer.get_analysis_statistics()
    print(f"\nEstatísticas:")
    print(f"Total de análises: {stats['total_analyses']}")
    print(f"Tempo médio de processamento: {stats['average_processing_time']:.3f}s")
    
    return analyzer

if __name__ == "__main__":
    main()

