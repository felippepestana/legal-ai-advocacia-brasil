#!/usr/bin/env python3
"""
Analisador Avançado de Documentos Jurídicos com IA
Versão aprimorada com funcionalidades expandidas e melhor integração de IA.
"""

import os
import re
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import PyPDF2
from openai import OpenAI

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentType(Enum):
    PETICAO_INICIAL = "Petição Inicial"
    CONTESTACAO = "Contestação"
    SENTENCA = "Sentença"
    ACORDAO = "Acórdão"
    INTIMACAO = "Intimação"
    DESPACHO = "Despacho"
    DECISAO_INTERLOCUTORIA = "Decisão Interlocutória"
    RECURSO = "Recurso"
    EMBARGOS = "Embargos"
    CONTRATO = "Contrato"
    PROCURACAO = "Procuração"
    OUTROS = "Outros"

class EntityType(Enum):
    CPF = "cpf"
    CNPJ = "cnpj"
    PROCESSO = "processo"
    VALOR_MONETARIO = "valor_monetario"
    DATA = "data"
    PRAZO = "prazo"
    PESSOA_FISICA = "pessoa_fisica"
    PESSOA_JURIDICA = "pessoa_juridica"
    ENDERECO = "endereco"
    EMAIL = "email"
    TELEFONE = "telefone"
    LEI = "lei"
    ARTIGO = "artigo"

class OpportunityType(Enum):
    RECURSO = "recurso"
    EMBARGOS = "embargos"
    EXECUCAO = "execucao"
    CUMPRIMENTO_SENTENCA = "cumprimento_sentenca"
    REVISAO_CONTRATUAL = "revisao_contratual"
    ACAO_CAUTELAR = "acao_cautelar"
    MANDADO_SEGURANCA = "mandado_seguranca"
    HABEAS_CORPUS = "habeas_corpus"

@dataclass
class ExtractedEntity:
    type: EntityType
    value: str
    confidence: float
    position: int
    context: str

@dataclass
class LegalOpportunity:
    type: OpportunityType
    description: str
    probability: float
    deadline: Optional[datetime]
    requirements: List[str]
    estimated_value: Optional[float]

@dataclass
class DocumentAnalysis:
    document_id: str
    document_type: DocumentType
    confidence_score: float
    extracted_entities: List[ExtractedEntity]
    opportunities: List[LegalOpportunity]
    summary: str
    key_points: List[str]
    risks: List[str]
    recommendations: List[str]
    analysis_timestamp: datetime
    processing_time: float

class AdvancedDocumentAnalyzer:
    """Analisador avançado de documentos jurídicos com IA."""
    
    def __init__(self):
        self.client = OpenAI()
        self.entity_patterns = self._initialize_patterns()
        self.classification_keywords = self._initialize_classification_keywords()
        
    def _initialize_patterns(self) -> Dict[EntityType, re.Pattern]:
        """Inicializa padrões regex para extração de entidades."""
        return {
            EntityType.CPF: re.compile(r'\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b'),
            EntityType.CNPJ: re.compile(r'\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b'),
            EntityType.PROCESSO: re.compile(r'\b\d{7}-?\d{2}\.?\d{4}\.?\d{1}\.?\d{2}\.?\d{4}\b'),
            EntityType.VALOR_MONETARIO: re.compile(r'R\$\s*[\d.,]+|\d+,\d{2}(?:\s*reais?)?'),
            EntityType.DATA: re.compile(r'\b\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}\b'),
            EntityType.EMAIL: re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            EntityType.TELEFONE: re.compile(r'\(?\d{2}\)?\s*\d{4,5}-?\d{4}'),
            EntityType.LEI: re.compile(r'Lei\s+n[ºo°]?\s*[\d.,/]+', re.IGNORECASE),
            EntityType.ARTIGO: re.compile(r'art(?:igo)?\.?\s*\d+[ºo°]?', re.IGNORECASE)
        }
    
    def _initialize_classification_keywords(self) -> Dict[DocumentType, List[str]]:
        """Inicializa palavras-chave para classificação de documentos."""
        return {
            DocumentType.PETICAO_INICIAL: [
                'petição inicial', 'ação de', 'requer', 'autor', 'réu', 'causa de pedir',
                'pedido', 'valor da causa', 'distribuição', 'citação'
            ],
            DocumentType.CONTESTACAO: [
                'contestação', 'impugnação', 'defesa', 'preliminar', 'mérito',
                'ilegitimidade', 'carência', 'prescrição', 'decadência'
            ],
            DocumentType.SENTENCA: [
                'sentença', 'julgo procedente', 'julgo improcedente', 'extingo',
                'condeno', 'absolvo', 'dispositivo', 'fundamentação'
            ],
            DocumentType.ACORDAO: [
                'acórdão', 'tribunal', 'relator', 'revisor', 'voto', 'ementa',
                'apelação', 'agravo', 'recurso especial', 'recurso extraordinário'
            ],
            DocumentType.INTIMACAO: [
                'intimação', 'fica intimado', 'prazo de', 'manifestar',
                'cumprir', 'comparecer', 'apresentar'
            ],
            DocumentType.DESPACHO: [
                'despacho', 'defiro', 'indefiro', 'determino', 'cite-se',
                'intime-se', 'cumpra-se', 'arquive-se'
            ],
            DocumentType.CONTRATO: [
                'contrato', 'contratante', 'contratado', 'cláusula', 'objeto',
                'prazo', 'valor', 'rescisão', 'vigência'
            ]
        }
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extrai texto de arquivo PDF."""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            logger.error(f"Erro ao extrair texto do PDF {file_path}: {e}")
            raise
    
    def extract_text_from_file(self, file_path: str) -> str:
        """Extrai texto de arquivo (TXT ou PDF)."""
        if file_path.lower().endswith('.pdf'):
            return self.extract_text_from_pdf(file_path)
        else:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    return file.read()
            except Exception as e:
                logger.error(f"Erro ao ler arquivo {file_path}: {e}")
                raise
    
    def classify_document(self, text: str) -> Tuple[DocumentType, float]:
        """Classifica o tipo de documento baseado no conteúdo."""
        text_lower = text.lower()
        scores = {}
        
        for doc_type, keywords in self.classification_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    score += 1
            scores[doc_type] = score / len(keywords) if keywords else 0
        
        # Encontra o tipo com maior pontuação
        best_type = max(scores, key=scores.get)
        confidence = scores[best_type]
        
        # Se a confiança for muito baixa, classifica como OUTROS
        if confidence < 0.1:
            return DocumentType.OUTROS, confidence
        
        return best_type, confidence
    
    def extract_entities(self, text: str) -> List[ExtractedEntity]:
        """Extrai entidades do texto usando regex e IA."""
        entities = []
        
        # Extração com regex
        for entity_type, pattern in self.entity_patterns.items():
            matches = pattern.finditer(text)
            for match in matches:
                # Contexto ao redor da entidade
                start = max(0, match.start() - 50)
                end = min(len(text), match.end() + 50)
                context = text[start:end].strip()
                
                entity = ExtractedEntity(
                    type=entity_type,
                    value=match.group().strip(),
                    confidence=0.9,  # Alta confiança para regex
                    position=match.start(),
                    context=context
                )
                entities.append(entity)
        
        # Extração adicional de pessoas físicas e jurídicas
        entities.extend(self._extract_names_with_ai(text))
        
        return entities
    
    def _extract_names_with_ai(self, text: str) -> List[ExtractedEntity]:
        """Extrai nomes de pessoas e empresas usando IA."""
        entities = []
        
        try:
            prompt = f"""
            Analise o texto jurídico abaixo e extraia:
            1. Nomes de pessoas físicas
            2. Nomes de empresas/pessoas jurídicas
            3. Endereços completos
            
            Retorne apenas uma lista JSON com objetos no formato:
            {{"type": "pessoa_fisica|pessoa_juridica|endereco", "value": "nome/endereço", "confidence": 0.0-1.0}}
            
            Texto:
            {text[:2000]}  # Limita o texto para evitar tokens excessivos
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
            )
            
            result = response.choices[0].message.content.strip()
            
            # Tenta extrair JSON da resposta
            import json
            try:
                extracted_data = json.loads(result)
                for item in extracted_data:
                    if item.get('type') == 'pessoa_fisica':
                        entity_type = EntityType.PESSOA_FISICA
                    elif item.get('type') == 'pessoa_juridica':
                        entity_type = EntityType.PESSOA_JURIDICA
                    elif item.get('type') == 'endereco':
                        entity_type = EntityType.ENDERECO
                    else:
                        continue
                    
                    entity = ExtractedEntity(
                        type=entity_type,
                        value=item.get('value', ''),
                        confidence=item.get('confidence', 0.7),
                        position=text.find(item.get('value', '')),
                        context=item.get('value', '')
                    )
                    entities.append(entity)
            except json.JSONDecodeError:
                logger.warning("Não foi possível extrair entidades com IA - resposta inválida")
                
        except Exception as e:
            logger.warning(f"Erro na extração de entidades com IA: {e}")
        
        return entities
    
    def identify_opportunities(self, text: str, document_type: DocumentType, entities: List[ExtractedEntity]) -> List[LegalOpportunity]:
        """Identifica oportunidades jurídicas no documento."""
        opportunities = []
        text_lower = text.lower()
        
        # Regras baseadas no tipo de documento
        if document_type == DocumentType.SENTENCA:
            if any(word in text_lower for word in ['procedente', 'condenação', 'condeno']):
                opportunities.append(LegalOpportunity(
                    type=OpportunityType.EXECUCAO,
                    description="Possibilidade de execução da sentença",
                    probability=0.85,
                    deadline=datetime.now() + timedelta(days=365*2),  # 2 anos para executar
                    requirements=["Trânsito em julgado", "Liquidação se necessário"],
                    estimated_value=self._extract_monetary_value(entities)
                ))
            
            if any(word in text_lower for word in ['improcedente', 'julgo improcedente']):
                opportunities.append(LegalOpportunity(
                    type=OpportunityType.RECURSO,
                    description="Possibilidade de recurso de apelação",
                    probability=0.75,
                    deadline=datetime.now() + timedelta(days=15),
                    requirements=["Preparo do recurso", "Razões recursais"],
                    estimated_value=None
                ))
        
        elif document_type == DocumentType.INTIMACAO:
            # Identifica prazos em intimações
            prazo_match = re.search(r'prazo de (\d+) dias?', text_lower)
            if prazo_match:
                dias = int(prazo_match.group(1))
                opportunities.append(LegalOpportunity(
                    type=OpportunityType.CUMPRIMENTO_SENTENCA,
                    description=f"Cumprimento de prazo de {dias} dias",
                    probability=1.0,
                    deadline=datetime.now() + timedelta(days=dias),
                    requirements=["Manifestação nos autos"],
                    estimated_value=None
                ))
        
        elif document_type == DocumentType.CONTRATO:
            # Análise de contratos para revisão
            if any(word in text_lower for word in ['juros', 'multa', 'cláusula penal']):
                opportunities.append(LegalOpportunity(
                    type=OpportunityType.REVISAO_CONTRATUAL,
                    description="Possível revisão de cláusulas abusivas",
                    probability=0.6,
                    deadline=None,
                    requirements=["Análise detalhada das cláusulas", "Fundamentação jurídica"],
                    estimated_value=None
                ))
        
        return opportunities
    
    def _extract_monetary_value(self, entities: List[ExtractedEntity]) -> Optional[float]:
        """Extrai valor monetário das entidades."""
        for entity in entities:
            if entity.type == EntityType.VALOR_MONETARIO:
                # Tenta converter o valor para float
                value_str = re.sub(r'[^\d,.]', '', entity.value)
                value_str = value_str.replace(',', '.')
                try:
                    return float(value_str)
                except ValueError:
                    continue
        return None
    
    def generate_ai_analysis(self, text: str, document_type: DocumentType) -> Tuple[str, List[str], List[str], List[str]]:
        """Gera análise com IA: resumo, pontos-chave, riscos e recomendações."""
        try:
            prompt = f"""
            Analise o seguinte documento jurídico do tipo "{document_type.value}" e forneça:
            
            1. RESUMO: Um resumo conciso do documento (máximo 200 palavras)
            2. PONTOS_CHAVE: Lista de 3-5 pontos mais importantes
            3. RISCOS: Lista de 2-4 riscos ou pontos de atenção
            4. RECOMENDAÇÕES: Lista de 3-5 recomendações práticas
            
            Formato de resposta (JSON):
            {{
                "resumo": "texto do resumo",
                "pontos_chave": ["ponto 1", "ponto 2", ...],
                "riscos": ["risco 1", "risco 2", ...],
                "recomendacoes": ["recomendação 1", "recomendação 2", ...]
            }}
            
            Documento:
            {text[:3000]}  # Limita para evitar excesso de tokens
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2
            )
            
            result = response.choices[0].message.content.strip()
            
            # Tenta extrair JSON da resposta
            import json
            analysis_data = json.loads(result)
            
            return (
                analysis_data.get('resumo', 'Resumo não disponível'),
                analysis_data.get('pontos_chave', []),
                analysis_data.get('riscos', []),
                analysis_data.get('recomendacoes', [])
            )
            
        except Exception as e:
            logger.error(f"Erro na análise com IA: {e}")
            return (
                "Resumo não disponível devido a erro na análise com IA",
                ["Análise manual necessária"],
                ["Verificar conectividade com IA"],
                ["Realizar análise manual do documento"]
            )
    
    def analyze_document(self, file_path: str, document_id: Optional[str] = None) -> DocumentAnalysis:
        """Analisa um documento jurídico de forma completa."""
        start_time = datetime.now()
        
        if document_id is None:
            document_id = os.path.basename(file_path)
        
        logger.info(f"Iniciando análise avançada do documento: {document_id}")
        
        try:
            # 1. Extração de texto
            text = self.extract_text_from_file(file_path)
            
            # 2. Classificação do documento
            document_type, confidence_score = self.classify_document(text)
            
            # 3. Extração de entidades
            entities = self.extract_entities(text)
            
            # 4. Identificação de oportunidades
            opportunities = self.identify_opportunities(text, document_type, entities)
            
            # 5. Análise com IA
            summary, key_points, risks, recommendations = self.generate_ai_analysis(text, document_type)
            
            # 6. Cálculo do tempo de processamento
            processing_time = (datetime.now() - start_time).total_seconds()
            
            analysis = DocumentAnalysis(
                document_id=document_id,
                document_type=document_type,
                confidence_score=confidence_score,
                extracted_entities=entities,
                opportunities=opportunities,
                summary=summary,
                key_points=key_points,
                risks=risks,
                recommendations=recommendations,
                analysis_timestamp=datetime.now(),
                processing_time=processing_time
            )
            
            logger.info(f"Análise avançada concluída para {document_id} em {processing_time:.2f}s")
            return analysis
            
        except Exception as e:
            logger.error(f"Erro na análise do documento {document_id}: {e}")
            raise
    
    def save_analysis(self, analysis: DocumentAnalysis, output_path: str):
        """Salva a análise em arquivo JSON."""
        try:
            # Converte para dicionário, tratando enums e datetime
            analysis_dict = asdict(analysis)
            
            # Converte enums para strings
            analysis_dict['document_type'] = analysis.document_type.value
            analysis_dict['analysis_timestamp'] = analysis.analysis_timestamp.isoformat()
            
            for entity in analysis_dict['extracted_entities']:
                entity['type'] = EntityType(entity['type']).value
            
            for opportunity in analysis_dict['opportunities']:
                opportunity['type'] = OpportunityType(opportunity['type']).value
                if opportunity['deadline']:
                    opportunity['deadline'] = opportunity['deadline'].isoformat()
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(analysis_dict, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Análise salva em: {output_path}")
            
        except Exception as e:
            logger.error(f"Erro ao salvar análise: {e}")
            raise

def main():
    """Função principal para demonstração."""
    analyzer = AdvancedDocumentAnalyzer()
    
    # Criar documento de exemplo se não existir
    example_doc = "/home/ubuntu/exemplo_sentenca_avancada.txt"
    if not os.path.exists(example_doc):
        with open(example_doc, "w", encoding="utf-8") as f:
            f.write("""
            SENTENÇA

            Processo n° 0012345-67.2025.8.26.0100
            Autor: MARIA DA SILVA, CPF 123.456.789-00
            Réu: EMPRESA XYZ LTDA, CNPJ 12.345.678/0001-90

            Vistos.

            MARIA DA SILVA ajuizou ação de cobrança contra EMPRESA XYZ LTDA, alegando 
            que a ré deixou de pagar o valor de R$ 25.000,00 referente a serviços prestados.

            A ré foi citada e apresentou contestação, alegando que os serviços não foram 
            prestados adequadamente.

            É o relatório. DECIDO.

            Analisando os autos, verifico que a autora comprovou a prestação dos serviços
            através dos documentos de fls. 15/30.

            A ré não logrou êxito em comprovar suas alegações.

            Ante o exposto, JULGO PROCEDENTE o pedido para condenar a ré ao pagamento 
            de R$ 25.000,00, corrigido monetariamente desde o vencimento e acrescido 
            de juros de mora de 1% ao mês desde a citação.

            Condeno a ré ao pagamento das custas processuais e honorários advocatícios 
            fixados em 10% sobre o valor da condenação.

            Publique-se. Registre-se. Intimem-se.

            São Paulo, 15 de setembro de 2025.

            Dr. João dos Santos
            Juiz de Direito
            """)
    
    # Analisar documento
    try:
        analysis = analyzer.analyze_document(example_doc)
        
        # Salvar análise
        output_file = "/home/ubuntu/analise_avancada_exemplo.json"
        analyzer.save_analysis(analysis, output_file)
        
        # Exibir resumo
        print(f"\n=== ANÁLISE AVANÇADA CONCLUÍDA ===")
        print(f"Documento: {analysis.document_id}")
        print(f"Tipo: {analysis.document_type.value}")
        print(f"Confiança: {analysis.confidence_score:.2f}")
        print(f"Entidades extraídas: {len(analysis.extracted_entities)}")
        print(f"Oportunidades identificadas: {len(analysis.opportunities)}")
        print(f"Tempo de processamento: {analysis.processing_time:.2f}s")
        
        print(f"\nResumo: {analysis.summary}")
        
        if analysis.opportunities:
            print(f"\nOportunidades:")
            for opp in analysis.opportunities:
                print(f"  - {opp.type.value}: {opp.description} (prob: {opp.probability:.0%})")
        
        print(f"\nAnálise salva em: {output_file}")
        
    except Exception as e:
        print(f"Erro na análise: {e}")

if __name__ == "__main__":
    main()

