#!/usr/bin/env python3
"""
Gerador de Documentos Jurídicos - Versão Melhorada
Implementa melhorias: mais templates, personalização avançada e integração com IA
"""

import json
import re
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import openai
from jinja2 import Template, Environment, FileSystemLoader
import time

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentType(Enum):
    """Tipos de documentos jurídicos"""
    PETICAO_INICIAL = "Petição Inicial"
    CONTESTACAO = "Contestação"
    RECURSO_APELACAO = "Recurso de Apelação"
    EMBARGOS_DECLARACAO = "Embargos de Declaração"
    AGRAVO_INSTRUMENTO = "Agravo de Instrumento"
    MANDADO_SEGURANCA = "Mandado de Segurança"
    HABEAS_CORPUS = "Habeas Corpus"
    ACAO_RESCISORIA = "Ação Rescisória"
    EXECUCAO = "Execução"
    CAUTELAR = "Cautelar"
    CONTRATO = "Contrato"
    PROCURACAO = "Procuração"
    PARECER = "Parecer Jurídico"
    NOTIFICACAO = "Notificação Extrajudicial"
    ACORDO = "Termo de Acordo"

class LegalArea(Enum):
    """Áreas do direito"""
    CIVIL = "Civil"
    TRABALHISTA = "Trabalhista"
    PENAL = "Penal"
    TRIBUTARIO = "Tributário"
    EMPRESARIAL = "Empresarial"
    CONSUMIDOR = "Consumidor"
    FAMILIA = "Família"
    PREVIDENCIARIO = "Previdenciário"
    ADMINISTRATIVO = "Administrativo"
    CONSTITUCIONAL = "Constitucional"

@dataclass
class DocumentTemplate:
    """Template de documento"""
    id: str
    name: str
    type: DocumentType
    area: LegalArea
    template_content: str
    required_fields: List[str]
    optional_fields: List[str]
    ai_assistance: bool = True
    complexity_level: str = "medium"  # basic, medium, advanced

@dataclass
class DocumentRequest:
    """Solicitação de geração de documento"""
    id: str
    template_id: str
    user_id: str
    data: Dict[str, Any]
    created_at: datetime
    ai_enhancement: bool = True
    custom_instructions: str = ""

@dataclass
class GeneratedDocument:
    """Documento gerado"""
    id: str
    request_id: str
    content: str
    metadata: Dict[str, Any]
    generated_at: datetime
    ai_enhanced: bool
    quality_score: float

class EnhancedTemplateLibrary:
    """Biblioteca aprimorada de templates"""
    
    def __init__(self):
        self.templates = self._load_templates()
        self.ai_prompts = self._load_ai_prompts()
    
    def _load_templates(self) -> Dict[str, DocumentTemplate]:
        """Carrega templates de documentos"""
        templates = {}
        
        # Template: Petição Inicial Civil
        templates["peticao_inicial_civil"] = DocumentTemplate(
            id="peticao_inicial_civil",
            name="Petição Inicial - Ação Civil",
            type=DocumentType.PETICAO_INICIAL,
            area=LegalArea.CIVIL,
            template_content=self._get_peticao_inicial_template(),
            required_fields=["autor", "reu", "fatos", "pedidos", "valor_causa", "advogado", "oab"],
            optional_fields=["testemunhas", "documentos", "jurisprudencia"],
            ai_assistance=True,
            complexity_level="medium"
        )
        
        # Template: Contestação
        templates["contestacao_civil"] = DocumentTemplate(
            id="contestacao_civil",
            name="Contestação - Ação Civil",
            type=DocumentType.CONTESTACAO,
            area=LegalArea.CIVIL,
            template_content=self._get_contestacao_template(),
            required_fields=["reu", "autor", "processo", "defesas", "advogado", "oab"],
            optional_fields=["preliminares", "reconvencao", "documentos"],
            ai_assistance=True,
            complexity_level="medium"
        )
        
        # Template: Recurso de Apelação
        templates["recurso_apelacao"] = DocumentTemplate(
            id="recurso_apelacao",
            name="Recurso de Apelação",
            type=DocumentType.RECURSO_APELACAO,
            area=LegalArea.CIVIL,
            template_content=self._get_recurso_template(),
            required_fields=["apelante", "apelado", "processo", "sentenca", "fundamentos", "pedidos"],
            optional_fields=["jurisprudencia", "doutrina", "efeito_suspensivo"],
            ai_assistance=True,
            complexity_level="advanced"
        )
        
        # Template: Contrato de Prestação de Serviços
        templates["contrato_servicos"] = DocumentTemplate(
            id="contrato_servicos",
            name="Contrato de Prestação de Serviços",
            type=DocumentType.CONTRATO,
            area=LegalArea.EMPRESARIAL,
            template_content=self._get_contrato_template(),
            required_fields=["contratante", "contratado", "objeto", "valor", "prazo", "pagamento"],
            optional_fields=["garantias", "penalidades", "rescisao"],
            ai_assistance=True,
            complexity_level="medium"
        )
        
        # Template: Procuração
        templates["procuracao"] = DocumentTemplate(
            id="procuracao",
            name="Procuração Ad Judicia",
            type=DocumentType.PROCURACAO,
            area=LegalArea.CIVIL,
            template_content=self._get_procuracao_template(),
            required_fields=["outorgante", "outorgado", "poderes", "oab"],
            optional_fields=["substabelecimento", "prazo"],
            ai_assistance=False,
            complexity_level="basic"
        )
        
        # Template: Notificação Extrajudicial
        templates["notificacao"] = DocumentTemplate(
            id="notificacao",
            name="Notificação Extrajudicial",
            type=DocumentType.NOTIFICACAO,
            area=LegalArea.CIVIL,
            template_content=self._get_notificacao_template(),
            required_fields=["notificante", "notificado", "motivo", "prazo"],
            optional_fields=["consequencias", "documentos"],
            ai_assistance=True,
            complexity_level="basic"
        )
        
        # Template: Parecer Jurídico
        templates["parecer"] = DocumentTemplate(
            id="parecer",
            name="Parecer Jurídico",
            type=DocumentType.PARECER,
            area=LegalArea.CIVIL,
            template_content=self._get_parecer_template(),
            required_fields=["consulente", "questao", "analise", "conclusao", "advogado"],
            optional_fields=["legislacao", "jurisprudencia", "doutrina"],
            ai_assistance=True,
            complexity_level="advanced"
        )
        
        return templates
    
    def _get_peticao_inicial_template(self) -> str:
        """Template de petição inicial"""
        return """
EXCELENTÍSSIMO SENHOR DOUTOR JUIZ DE DIREITO DA {{ vara }} VARA {{ especialidade }} DA COMARCA DE {{ comarca }}

{{ autor.nome }}, {{ autor.nacionalidade }}, {{ autor.estado_civil }}, {{ autor.profissao }}, portador do CPF nº {{ autor.cpf }}, residente e domiciliado na {{ autor.endereco }}, por seu advogado que esta subscreve, vem respeitosamente à presença de Vossa Excelência propor a presente

{{ tipo_acao }}

em face de {{ reu.nome }}, {{ reu.qualificacao }}, pelos fatos e fundamentos a seguir expostos:

DOS FATOS

{{ fatos }}

DO DIREITO

{{ fundamentacao_juridica }}

DOS PEDIDOS

Ante o exposto, requer:

{% for pedido in pedidos %}
{{ loop.index }}) {{ pedido }};
{% endfor %}

Protesta provar o alegado por todos os meios de prova em direito admitidos.

Dá-se à causa o valor de R$ {{ valor_causa }}.

Termos em que pede deferimento.

{{ local }}, {{ data }}.

{{ advogado.nome }}
OAB/{{ advogado.estado }} {{ advogado.numero }}
"""
    
    def _get_contestacao_template(self) -> str:
        """Template de contestação"""
        return """
EXCELENTÍSSIMO SENHOR DOUTOR JUIZ DE DIREITO DA {{ vara }} VARA {{ especialidade }} DA COMARCA DE {{ comarca }}

Processo nº {{ processo }}

{{ reu.nome }}, já qualificado nos autos em epígrafe, por seu advogado que esta subscreve, vem respeitosamente à presença de Vossa Excelência apresentar

CONTESTAÇÃO

em face da ação proposta por {{ autor.nome }}, pelas razões de fato e de direito a seguir expostas:

{% if preliminares %}
DAS PRELIMINARES

{% for preliminar in preliminares %}
{{ preliminar }}
{% endfor %}
{% endif %}

DO MÉRITO

{{ defesa_merito }}

DOS PEDIDOS

Ante o exposto, requer:

a) O acolhimento das preliminares arguidas, com a consequente extinção do processo sem resolução do mérito;
b) Subsidiariamente, a total improcedência dos pedidos formulados na inicial;
{% for pedido in pedidos_adicionais %}
c) {{ pedido }};
{% endfor %}

Protesta provar o alegado por todos os meios de prova em direito admitidos.

Termos em que pede deferimento.

{{ local }}, {{ data }}.

{{ advogado.nome }}
OAB/{{ advogado.estado }} {{ advogado.numero }}
"""
    
    def _get_recurso_template(self) -> str:
        """Template de recurso de apelação"""
        return """
EXCELENTÍSSIMO SENHOR DESEMBARGADOR RELATOR DO EGRÉGIO TRIBUNAL DE JUSTIÇA DO ESTADO DE {{ estado }}

Processo nº {{ processo }}

{{ apelante.nome }}, já qualificado nos autos em epígrafe, irresignado com a r. sentença de fls. {{ folhas_sentenca }}, que {{ dispositivo_sentenca }}, vem, tempestivamente, por seu advogado que esta subscreve, interpor

RECURSO DE APELAÇÃO

pelas razões de fato e de direito a seguir expostas:

DO CABIMENTO

O presente recurso é cabível nos termos do art. 1009 do Código de Processo Civil.

DOS FUNDAMENTOS

{{ fundamentos_recurso }}

{% if jurisprudencia %}
DA JURISPRUDÊNCIA

{{ jurisprudencia }}
{% endif %}

DOS PEDIDOS

Ante o exposto, requer:

{% for pedido in pedidos %}
{{ loop.index }}) {{ pedido }};
{% endfor %}

Termos em que pede provimento.

{{ local }}, {{ data }}.

{{ advogado.nome }}
OAB/{{ advogado.estado }} {{ advogado.numero }}
"""
    
    def _get_contrato_template(self) -> str:
        """Template de contrato"""
        return """
CONTRATO DE {{ tipo_contrato }}

Pelo presente instrumento particular, de um lado {{ contratante.nome }}, {{ contratante.qualificacao }}, doravante denominado CONTRATANTE, e de outro lado {{ contratado.nome }}, {{ contratado.qualificacao }}, doravante denominado CONTRATADO, têm entre si justo e acordado o presente contrato, que se regerá pelas cláusulas e condições seguintes:

CLÁUSULA 1ª - DO OBJETO
{{ objeto }}

CLÁUSULA 2ª - DO VALOR E FORMA DE PAGAMENTO
{{ valor_pagamento }}

CLÁUSULA 3ª - DO PRAZO
{{ prazo }}

CLÁUSULA 4ª - DAS OBRIGAÇÕES DO CONTRATANTE
{{ obrigacoes_contratante }}

CLÁUSULA 5ª - DAS OBRIGAÇÕES DO CONTRATADO
{{ obrigacoes_contratado }}

{% if garantias %}
CLÁUSULA 6ª - DAS GARANTIAS
{{ garantias }}
{% endif %}

{% if penalidades %}
CLÁUSULA 7ª - DAS PENALIDADES
{{ penalidades }}
{% endif %}

CLÁUSULA FINAL - DO FORO
Fica eleito o foro da comarca de {{ foro }} para dirimir quaisquer questões oriundas do presente contrato.

E por estarem assim justos e contratados, assinam o presente instrumento em duas vias de igual teor e forma.

{{ local }}, {{ data }}.

_________________________                    _________________________
{{ contratante.nome }}                       {{ contratado.nome }}
CONTRATANTE                                  CONTRATADO

Testemunhas:
1. _________________________
2. _________________________
"""
    
    def _get_procuracao_template(self) -> str:
        """Template de procuração"""
        return """
PROCURAÇÃO

{{ outorgante.nome }}, {{ outorgante.qualificacao }}, pelo presente instrumento de mandato, nomeia e constitui seu bastante procurador {{ outorgado.nome }}, advogado, inscrito na OAB/{{ outorgado.estado }} sob o nº {{ outorgado.oab }}, com escritório na {{ outorgado.endereco }}, a quem confere poderes para:

{{ poderes }}

{% if substabelecimento %}
Poderes de substabelecimento: {{ substabelecimento }}
{% endif %}

{{ local }}, {{ data }}.

_________________________
{{ outorgante.nome }}
OUTORGANTE
"""
    
    def _get_notificacao_template(self) -> str:
        """Template de notificação extrajudicial"""
        return """
NOTIFICAÇÃO EXTRAJUDICIAL

{{ notificante.nome }}, {{ notificante.qualificacao }}, vem por meio desta NOTIFICAR {{ notificado.nome }}, {{ notificado.qualificacao }}, para que:

{{ motivo }}

Fica estabelecido o prazo de {{ prazo }} para cumprimento da presente notificação.

{% if consequencias %}
O descumprimento da presente notificação acarretará:
{{ consequencias }}
{% endif %}

{{ local }}, {{ data }}.

_________________________
{{ notificante.nome }}
NOTIFICANTE
"""
    
    def _get_parecer_template(self) -> str:
        """Template de parecer jurídico"""
        return """
PARECER JURÍDICO

CONSULENTE: {{ consulente }}
ASSUNTO: {{ assunto }}

1. DA CONSULTA

{{ questao }}

2. DA ANÁLISE JURÍDICA

{{ analise }}

{% if legislacao %}
3. DA LEGISLAÇÃO APLICÁVEL

{{ legislacao }}
{% endif %}

{% if jurisprudencia %}
4. DA JURISPRUDÊNCIA

{{ jurisprudencia }}
{% endif %}

5. CONCLUSÃO

{{ conclusao }}

{{ local }}, {{ data }}.

{{ advogado.nome }}
OAB/{{ advogado.estado }} {{ advogado.numero }}
"""
    
    def _load_ai_prompts(self) -> Dict[str, str]:
        """Carrega prompts para IA"""
        return {
            "enhance_facts": """
            Você é um advogado especialista. Aprimore a narrativa dos fatos apresentados, 
            mantendo a veracidade mas tornando-a mais clara, persuasiva e juridicamente relevante.
            Use linguagem técnica apropriada e estruture de forma lógica.
            """,
            
            "generate_legal_basis": """
            Com base nos fatos apresentados, sugira a fundamentação jurídica adequada,
            incluindo artigos de lei, jurisprudência relevante e doutrina aplicável.
            Seja específico e cite as fontes legais pertinentes.
            """,
            
            "improve_arguments": """
            Aprimore os argumentos jurídicos apresentados, tornando-os mais sólidos,
            persuasivos e tecnicamente corretos. Adicione citações legais quando apropriado.
            """,
            
            "review_document": """
            Revise o documento jurídico apresentado, identificando possíveis melhorias
            na estrutura, argumentação, fundamentação legal e clareza da linguagem.
            Sugira correções e aprimoramentos.
            """
        }
    
    def get_template(self, template_id: str) -> Optional[DocumentTemplate]:
        """Retorna template específico"""
        return self.templates.get(template_id)
    
    def list_templates(self, area: LegalArea = None, doc_type: DocumentType = None) -> List[DocumentTemplate]:
        """Lista templates filtrados"""
        templates = list(self.templates.values())
        
        if area:
            templates = [t for t in templates if t.area == area]
        
        if doc_type:
            templates = [t for t in templates if t.type == doc_type]
        
        return templates

class AIEnhancementEngine:
    """Motor de aprimoramento com IA"""
    
    def __init__(self):
        self.client = openai.OpenAI()
        self.template_library = EnhancedTemplateLibrary()
    
    def enhance_content(self, content: str, enhancement_type: str, context: Dict[str, Any] = None) -> str:
        """Aprimora conteúdo usando IA"""
        prompts = self.template_library.ai_prompts
        
        if enhancement_type not in prompts:
            return content
        
        system_prompt = prompts[enhancement_type]
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Conteúdo para aprimorar: {content}"}
                ],
                max_tokens=1500,
                temperature=0.3
            )
            
            enhanced_content = response.choices[0].message.content
            return enhanced_content
            
        except Exception as e:
            logger.error(f"Erro no aprimoramento com IA: {e}")
            return content
    
    def generate_legal_basis(self, facts: str, area: LegalArea) -> str:
        """Gera fundamentação jurídica baseada nos fatos"""
        area_context = {
            LegalArea.CIVIL: "Direito Civil - Código Civil, responsabilidade civil, contratos",
            LegalArea.TRABALHISTA: "Direito do Trabalho - CLT, direitos trabalhistas",
            LegalArea.CONSUMIDOR: "Direito do Consumidor - CDC, relações de consumo",
            LegalArea.PENAL: "Direito Penal - Código Penal, processo penal",
            LegalArea.TRIBUTARIO: "Direito Tributário - CTN, legislação fiscal"
        }
        
        context = area_context.get(area, "Direito em geral")
        
        prompt = f"""
        Você é um advogado especialista em {context}.
        Com base nos fatos apresentados, forneça a fundamentação jurídica adequada,
        incluindo artigos de lei específicos, princípios jurídicos aplicáveis e
        possível jurisprudência relevante.
        
        Fatos: {facts}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": "Você é um advogado especialista em direito brasileiro."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Erro na geração de fundamentação: {e}")
            return "Fundamentação jurídica a ser desenvolvida."
    
    def calculate_quality_score(self, document: str, template: DocumentTemplate) -> float:
        """Calcula score de qualidade do documento"""
        score = 0.0
        
        # Verifica presença de campos obrigatórios
        required_present = 0
        for field in template.required_fields:
            if field.lower() in document.lower():
                required_present += 1
        
        field_score = (required_present / len(template.required_fields)) * 0.4
        score += field_score
        
        # Verifica estrutura do documento
        structure_indicators = ["dos fatos", "do direito", "dos pedidos", "ante o exposto"]
        structure_present = sum(1 for indicator in structure_indicators if indicator in document.lower())
        structure_score = (structure_present / len(structure_indicators)) * 0.3
        score += structure_score
        
        # Verifica qualidade da linguagem
        language_indicators = ["artigo", "lei", "código", "jurisprudência", "tribunal"]
        language_present = sum(1 for indicator in language_indicators if indicator in document.lower())
        language_score = min(language_present / 3, 1.0) * 0.3
        score += language_score
        
        return min(score, 1.0)

class EnhancedDocumentGenerator:
    """Gerador aprimorado de documentos"""
    
    def __init__(self):
        self.template_library = EnhancedTemplateLibrary()
        self.ai_engine = AIEnhancementEngine()
        self.jinja_env = Environment()
        self.generated_documents = {}
    
    def generate_document(self, request: DocumentRequest) -> GeneratedDocument:
        """Gera documento baseado na solicitação"""
        start_time = time.time()
        
        # Obtém template
        template = self.template_library.get_template(request.template_id)
        if not template:
            raise ValueError(f"Template {request.template_id} não encontrado")
        
        logger.info(f"Gerando documento: {template.name}")
        
        # Prepara dados
        data = self._prepare_data(request.data, template)
        
        # Aplica aprimoramentos com IA se solicitado
        if request.ai_enhancement and template.ai_assistance:
            data = self._apply_ai_enhancements(data, template, request.custom_instructions)
        
        # Renderiza template
        jinja_template = self.jinja_env.from_string(template.template_content)
        content = jinja_template.render(**data)
        
        # Calcula score de qualidade
        quality_score = self.ai_engine.calculate_quality_score(content, template)
        
        # Cria documento gerado
        document = GeneratedDocument(
            id=f"doc_{int(time.time())}_{request.user_id}",
            request_id=request.id,
            content=content,
            metadata={
                "template_id": template.id,
                "template_name": template.name,
                "document_type": template.type.value,
                "legal_area": template.area.value,
                "ai_enhanced": request.ai_enhancement and template.ai_assistance,
                "generation_time": time.time() - start_time,
                "word_count": len(content.split()),
                "character_count": len(content)
            },
            generated_at=datetime.now(),
            ai_enhanced=request.ai_enhancement and template.ai_assistance,
            quality_score=quality_score
        )
        
        self.generated_documents[document.id] = document
        
        logger.info(f"Documento gerado com sucesso. Score: {quality_score:.2f}")
        
        return document
    
    def _prepare_data(self, raw_data: Dict[str, Any], template: DocumentTemplate) -> Dict[str, Any]:
        """Prepara dados para renderização"""
        data = raw_data.copy()
        
        # Adiciona dados padrão
        data.setdefault("local", "São Paulo")
        data.setdefault("data", datetime.now().strftime("%d de %B de %Y"))
        data.setdefault("vara", "1ª")
        data.setdefault("especialidade", "CÍVEL")
        data.setdefault("comarca", "SÃO PAULO")
        
        # Converte datas para formato brasileiro
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.strftime("%d/%m/%Y")
        
        return data
    
    def _apply_ai_enhancements(self, data: Dict[str, Any], template: DocumentTemplate, 
                              custom_instructions: str) -> Dict[str, Any]:
        """Aplica aprimoramentos com IA"""
        enhanced_data = data.copy()
        
        # Aprimora fatos se presente
        if "fatos" in data and data["fatos"]:
            enhanced_data["fatos"] = self.ai_engine.enhance_content(
                data["fatos"], "enhance_facts"
            )
        
        # Gera fundamentação jurídica se não presente
        if "fundamentacao_juridica" not in data or not data["fundamentacao_juridica"]:
            if "fatos" in data:
                enhanced_data["fundamentacao_juridica"] = self.ai_engine.generate_legal_basis(
                    data["fatos"], template.area
                )
        
        # Aprimora argumentos se presente
        if "defesa_merito" in data and data["defesa_merito"]:
            enhanced_data["defesa_merito"] = self.ai_engine.enhance_content(
                data["defesa_merito"], "improve_arguments"
            )
        
        # Aplica instruções customizadas
        if custom_instructions:
            for key in ["fatos", "fundamentacao_juridica", "defesa_merito"]:
                if key in enhanced_data:
                    enhanced_data[key] = self._apply_custom_instructions(
                        enhanced_data[key], custom_instructions
                    )
        
        return enhanced_data
    
    def _apply_custom_instructions(self, content: str, instructions: str) -> str:
        """Aplica instruções customizadas ao conteúdo"""
        prompt = f"""
        Aplique as seguintes instruções ao conteúdo jurídico:
        
        Instruções: {instructions}
        
        Conteúdo: {content}
        
        Retorne o conteúdo modificado conforme as instruções.
        """
        
        try:
            response = self.ai_engine.client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": "Você é um advogado especialista em redação jurídica."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Erro na aplicação de instruções customizadas: {e}")
            return content
    
    def create_document_request(self, template_id: str, user_id: str, data: Dict[str, Any],
                               ai_enhancement: bool = True, custom_instructions: str = "") -> DocumentRequest:
        """Cria solicitação de documento"""
        request = DocumentRequest(
            id=f"req_{int(time.time())}_{user_id}",
            template_id=template_id,
            user_id=user_id,
            data=data,
            ai_enhancement=ai_enhancement,
            custom_instructions=custom_instructions,
            created_at=datetime.now()
        )
        
        return request
    
    def get_document(self, document_id: str) -> Optional[GeneratedDocument]:
        """Retorna documento gerado"""
        return self.generated_documents.get(document_id)
    
    def list_documents(self, user_id: str = None) -> List[GeneratedDocument]:
        """Lista documentos gerados"""
        documents = list(self.generated_documents.values())
        
        if user_id:
            # Filtra por user_id através do request_id (simplificado)
            documents = [d for d in documents if user_id in d.request_id]
        
        return sorted(documents, key=lambda x: x.generated_at, reverse=True)
    
    def get_generation_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas de geração"""
        documents = list(self.generated_documents.values())
        
        if not documents:
            return {"message": "Nenhum documento gerado ainda"}
        
        # Estatísticas básicas
        total_docs = len(documents)
        ai_enhanced_docs = sum(1 for d in documents if d.ai_enhanced)
        avg_quality = sum(d.quality_score for d in documents) / total_docs
        
        # Tipos de documento mais gerados
        doc_types = {}
        for doc in documents:
            doc_type = doc.metadata.get("document_type", "Desconhecido")
            doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
        
        # Tempo médio de geração
        avg_generation_time = sum(d.metadata.get("generation_time", 0) for d in documents) / total_docs
        
        return {
            "total_documents": total_docs,
            "ai_enhanced_documents": ai_enhanced_docs,
            "ai_enhancement_rate": (ai_enhanced_docs / total_docs) * 100,
            "average_quality_score": round(avg_quality, 2),
            "average_generation_time": round(avg_generation_time, 2),
            "document_types": doc_types,
            "total_words_generated": sum(d.metadata.get("word_count", 0) for d in documents)
        }

def main():
    """Função principal para demonstração"""
    print("=== Gerador de Documentos Jurídicos - Versão Melhorada ===")
    
    # Cria instância do gerador
    generator = EnhancedDocumentGenerator()
    
    # Lista templates disponíveis
    templates = generator.template_library.list_templates()
    print(f"\nTemplates disponíveis ({len(templates)}):")
    for template in templates:
        print(f"- {template.name} ({template.area.value})")
    
    # Dados de exemplo para petição inicial
    dados_peticao = {
        "autor": {
            "nome": "JOÃO SILVA",
            "nacionalidade": "brasileiro",
            "estado_civil": "casado",
            "profissao": "empresário",
            "cpf": "123.456.789-10",
            "endereco": "Rua das Flores, 123, São Paulo/SP"
        },
        "reu": {
            "nome": "BANCO XYZ S.A.",
            "qualificacao": "pessoa jurídica de direito privado, CNPJ 12.345.678/0001-90"
        },
        "tipo_acao": "AÇÃO DE INDENIZAÇÃO POR DANOS MORAIS",
        "fatos": "O autor teve seu nome indevidamente inscrito nos órgãos de proteção ao crédito pelo réu, sem que houvesse débito pendente.",
        "pedidos": [
            "A condenação do réu ao pagamento de indenização por danos morais no valor de R$ 20.000,00",
            "A exclusão do nome do autor dos órgãos de proteção ao crédito"
        ],
        "valor_causa": "20.000,00",
        "advogado": {
            "nome": "Dr. Carlos Santos",
            "estado": "SP",
            "numero": "123456"
        }
    }
    
    # Cria solicitação de documento
    request = generator.create_document_request(
        template_id="peticao_inicial_civil",
        user_id="usuario_teste",
        data=dados_peticao,
        ai_enhancement=True,
        custom_instructions="Use linguagem mais técnica e adicione mais fundamentação jurídica"
    )
    
    print(f"\nGerando petição inicial...")
    
    # Gera documento
    document = generator.generate_document(request)
    
    print(f"Documento gerado: {document.id}")
    print(f"Tipo: {document.metadata['document_type']}")
    print(f"Score de qualidade: {document.quality_score:.2f}")
    print(f"Aprimorado com IA: {document.ai_enhanced}")
    print(f"Tempo de geração: {document.metadata['generation_time']:.2f}s")
    print(f"Palavras: {document.metadata['word_count']}")
    
    # Mostra trecho do documento
    print(f"\nTrecho do documento:")
    print(document.content[:500] + "...")
    
    # Gera mais alguns documentos para estatísticas
    print(f"\nGerando documentos adicionais...")
    
    # Contestação
    dados_contestacao = {
        "reu": {"nome": "EMPRESA ABC LTDA"},
        "autor": {"nome": "MARIA SANTOS"},
        "processo": "1234567-89.2024.8.26.0100",
        "defesa_merito": "A empresa ré nega os fatos alegados na inicial, pois agiu dentro da legalidade.",
        "pedidos_adicionais": ["A condenação do autor ao pagamento de honorários advocatícios"],
        "advogado": {"nome": "Dra. Ana Costa", "estado": "SP", "numero": "654321"}
    }
    
    request2 = generator.create_document_request(
        template_id="contestacao_civil",
        user_id="usuario_teste",
        data=dados_contestacao
    )
    
    document2 = generator.generate_document(request2)
    
    # Contrato
    dados_contrato = {
        "tipo_contrato": "PRESTAÇÃO DE SERVIÇOS ADVOCATÍCIOS",
        "contratante": {"nome": "EMPRESA XYZ LTDA", "qualificacao": "pessoa jurídica"},
        "contratado": {"nome": "ESCRITÓRIO DE ADVOCACIA ABC", "qualificacao": "sociedade de advogados"},
        "objeto": "Prestação de serviços jurídicos na área cível",
        "valor_pagamento": "O valor dos serviços será de R$ 5.000,00 mensais",
        "prazo": "12 meses a partir da assinatura",
        "obrigacoes_contratante": "Fornecer todas as informações necessárias",
        "obrigacoes_contratado": "Prestar os serviços com qualidade e pontualidade",
        "foro": "São Paulo"
    }
    
    request3 = generator.create_document_request(
        template_id="contrato_servicos",
        user_id="usuario_teste",
        data=dados_contrato,
        ai_enhancement=False
    )
    
    document3 = generator.generate_document(request3)
    
    # Estatísticas
    stats = generator.get_generation_statistics()
    print(f"\n--- Estatísticas ---")
    print(f"Total de documentos: {stats['total_documents']}")
    print(f"Taxa de aprimoramento com IA: {stats['ai_enhancement_rate']:.1f}%")
    print(f"Score médio de qualidade: {stats['average_quality_score']}")
    print(f"Tempo médio de geração: {stats['average_generation_time']:.2f}s")
    print(f"Total de palavras geradas: {stats['total_words_generated']}")
    
    return generator

if __name__ == "__main__":
    main()

