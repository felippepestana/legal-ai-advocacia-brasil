#!/usr/bin/env python3
"""
Gerador Automático de Documentos Jurídicos com IA
Sistema para geração de petições, contratos e outros documentos jurídicos usando templates e IA.
"""

import os
import json
import uuid
import logging
from datetime import datetime, date
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import re
from openai import OpenAI

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentType(Enum):
    PETICAO_INICIAL = "peticao_inicial"
    CONTESTACAO = "contestacao"
    RECURSO_APELACAO = "recurso_apelacao"
    EMBARGOS_DECLARACAO = "embargos_declaracao"
    CONTRATO_PRESTACAO_SERVICOS = "contrato_prestacao_servicos"
    CONTRATO_COMPRA_VENDA = "contrato_compra_venda"
    PROCURACAO = "procuracao"
    ACORDO_EXTRAJUDICIAL = "acordo_extrajudicial"
    PARECER_JURIDICO = "parecer_juridico"
    NOTIFICACAO_EXTRAJUDICIAL = "notificacao_extrajudicial"

class DocumentCategory(Enum):
    PROCESSUAL = "processual"
    CONTRATUAL = "contratual"
    CONSULTIVO = "consultivo"
    EXTRAJUDICIAL = "extrajudicial"

@dataclass
class DocumentTemplate:
    template_id: str
    name: str
    document_type: DocumentType
    category: DocumentCategory
    description: str
    template_content: str
    required_fields: List[str]
    optional_fields: List[str]
    legal_requirements: List[str]
    created_at: datetime
    updated_at: datetime

@dataclass
class DocumentData:
    # Dados das partes
    autor_nome: Optional[str] = None
    autor_cpf_cnpj: Optional[str] = None
    autor_endereco: Optional[str] = None
    autor_profissao: Optional[str] = None
    
    reu_nome: Optional[str] = None
    reu_cpf_cnpj: Optional[str] = None
    reu_endereco: Optional[str] = None
    
    # Dados do advogado
    advogado_nome: Optional[str] = None
    advogado_oab: Optional[str] = None
    advogado_endereco: Optional[str] = None
    
    # Dados processuais
    processo_numero: Optional[str] = None
    tribunal: Optional[str] = None
    vara: Optional[str] = None
    juiz: Optional[str] = None
    
    # Dados do caso
    causa_pedir: Optional[str] = None
    pedidos: Optional[List[str]] = None
    valor_causa: Optional[float] = None
    fatos: Optional[str] = None
    fundamentos_juridicos: Optional[List[str]] = None
    
    # Dados contratuais
    objeto_contrato: Optional[str] = None
    prazo_contrato: Optional[str] = None
    valor_contrato: Optional[float] = None
    forma_pagamento: Optional[str] = None
    
    # Dados gerais
    data_documento: Optional[date] = None
    local: Optional[str] = None
    
    def __post_init__(self):
        if self.pedidos is None:
            self.pedidos = []
        if self.fundamentos_juridicos is None:
            self.fundamentos_juridicos = []
        if self.data_documento is None:
            self.data_documento = date.today()

@dataclass
class GeneratedDocument:
    document_id: str
    template_id: str
    document_type: DocumentType
    title: str
    content: str
    data_used: DocumentData
    generated_at: datetime
    generated_by: str
    file_path: Optional[str] = None

class DocumentTemplateManager:
    """Gerenciador de templates de documentos jurídicos."""
    
    def __init__(self):
        self.templates: Dict[str, DocumentTemplate] = {}
        self._initialize_default_templates()
    
    def _initialize_default_templates(self):
        """Inicializa templates padrão."""
        
        # Template de Petição Inicial
        peticao_template = DocumentTemplate(
            template_id="peticao_inicial_001",
            name="Petição Inicial - Ação de Cobrança",
            document_type=DocumentType.PETICAO_INICIAL,
            category=DocumentCategory.PROCESSUAL,
            description="Template para petição inicial de ação de cobrança",
            template_content="""
EXCELENTÍSSIMO(A) SENHOR(A) DOUTOR(A) JUIZ(A) DE DIREITO DA {vara}

{autor_nome}, {autor_profissao}, portador(a) do CPF/CNPJ {autor_cpf_cnpj}, residente e domiciliado(a) na {autor_endereco}, por seu advogado que esta subscreve (OAB {advogado_oab}), vem, respeitosamente, à presença de Vossa Excelência, propor

AÇÃO DE COBRANÇA

em face de {reu_nome}, pessoa {reu_tipo}, inscrita no CPF/CNPJ sob o nº {reu_cpf_cnpj}, com endereço na {reu_endereco}, pelos fatos e fundamentos jurídicos a seguir expostos:

I - DOS FATOS

{fatos}

II - DO DIREITO

{fundamentos_juridicos}

III - DOS PEDIDOS

Diante do exposto, requer-se:

{pedidos}

Dá-se à causa o valor de R$ {valor_causa}.

Termos em que,
Pede deferimento.

{local}, {data_documento}.

_________________________________
{advogado_nome}
OAB {advogado_oab}
            """,
            required_fields=[
                "vara", "autor_nome", "autor_cpf_cnpj", "autor_endereco", "autor_profissao",
                "reu_nome", "reu_cpf_cnpj", "reu_endereco", "advogado_nome", "advogado_oab",
                "fatos", "fundamentos_juridicos", "pedidos", "valor_causa", "local", "data_documento"
            ],
            optional_fields=["processo_numero"],
            legal_requirements=[
                "Qualificação completa das partes",
                "Causa de pedir e pedido",
                "Valor da causa",
                "Assinatura do advogado"
            ],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Template de Contestação
        contestacao_template = DocumentTemplate(
            template_id="contestacao_001",
            name="Contestação - Defesa Geral",
            document_type=DocumentType.CONTESTACAO,
            category=DocumentCategory.PROCESSUAL,
            description="Template para contestação com defesa geral",
            template_content="""
EXCELENTÍSSIMO(A) SENHOR(A) DOUTOR(A) JUIZ(A) DE DIREITO DA {vara}

Processo nº {processo_numero}

{reu_nome}, já qualificado(a) nos autos da ação que lhe move {autor_nome}, vem, por seu advogado que esta subscreve, tempestivamente, apresentar

CONTESTAÇÃO

pelos fatos e fundamentos jurídicos a seguir expostos:

I - DAS PRELIMINARES

{preliminares}

II - DO MÉRITO

{defesa_merito}

III - DOS PEDIDOS

Diante do exposto, requer-se:

a) O acolhimento das preliminares arguidas, com a consequente extinção do processo sem resolução do mérito;

b) Subsidiariamente, a total improcedência dos pedidos formulados na inicial;

{pedidos_adicionais}

Protesta por todos os meios de prova em direito admitidos.

Termos em que,
Pede deferimento.

{local}, {data_documento}.

_________________________________
{advogado_nome}
OAB {advogado_oab}
            """,
            required_fields=[
                "vara", "processo_numero", "reu_nome", "autor_nome", "advogado_nome", "advogado_oab",
                "preliminares", "defesa_merito", "local", "data_documento"
            ],
            optional_fields=["pedidos_adicionais"],
            legal_requirements=[
                "Tempestividade da contestação",
                "Impugnação específica dos fatos",
                "Fundamentação jurídica"
            ],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Template de Contrato de Prestação de Serviços
        contrato_template = DocumentTemplate(
            template_id="contrato_prestacao_001",
            name="Contrato de Prestação de Serviços",
            document_type=DocumentType.CONTRATO_PRESTACAO_SERVICOS,
            category=DocumentCategory.CONTRATUAL,
            description="Template para contrato de prestação de serviços",
            template_content="""
CONTRATO DE PRESTAÇÃO DE SERVIÇOS

CONTRATANTE: {autor_nome}, {autor_profissao}, portador(a) do CPF/CNPJ {autor_cpf_cnpj}, residente e domiciliado(a) na {autor_endereco}.

CONTRATADO: {reu_nome}, portador(a) do CPF/CNPJ {reu_cpf_cnpj}, residente e domiciliado(a) na {reu_endereco}.

As partes acima qualificadas celebram o presente contrato, que se regerá pelas cláusulas seguintes:

CLÁUSULA 1ª - DO OBJETO
O presente contrato tem por objeto {objeto_contrato}.

CLÁUSULA 2ª - DO PRAZO
O prazo para execução dos serviços será de {prazo_contrato}, contado a partir da assinatura deste contrato.

CLÁUSULA 3ª - DO VALOR E FORMA DE PAGAMENTO
O valor total dos serviços é de R$ {valor_contrato}, que será pago da seguinte forma: {forma_pagamento}.

CLÁUSULA 4ª - DAS OBRIGAÇÕES DO CONTRATADO
São obrigações do CONTRATADO:
a) Executar os serviços com qualidade e dentro do prazo estabelecido;
b) Manter sigilo sobre informações confidenciais;
c) Comunicar imediatamente qualquer impedimento para execução dos serviços.

CLÁUSULA 5ª - DAS OBRIGAÇÕES DO CONTRATANTE
São obrigações do CONTRATANTE:
a) Efetuar o pagamento nas datas acordadas;
b) Fornecer as informações necessárias para execução dos serviços;
c) Disponibilizar os recursos necessários quando aplicável.

CLÁUSULA 6ª - DA RESCISÃO
O presente contrato poderá ser rescindido por qualquer das partes, mediante aviso prévio de 30 (trinta) dias.

CLÁUSULA 7ª - DO FORO
Fica eleito o foro da comarca de {local} para dirimir quaisquer questões oriundas do presente contrato.

E por estarem assim justos e contratados, assinam o presente instrumento em duas vias de igual teor.

{local}, {data_documento}.

_________________________          _________________________
{autor_nome}                       {reu_nome}
CONTRATANTE                        CONTRATADO

Testemunhas:
1. _________________________
2. _________________________
            """,
            required_fields=[
                "autor_nome", "autor_profissao", "autor_cpf_cnpj", "autor_endereco",
                "reu_nome", "reu_cpf_cnpj", "reu_endereco", "objeto_contrato",
                "prazo_contrato", "valor_contrato", "forma_pagamento", "local", "data_documento"
            ],
            optional_fields=[],
            legal_requirements=[
                "Qualificação completa das partes",
                "Objeto claramente definido",
                "Prazo e valor especificados",
                "Assinatura das partes"
            ],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Adicionar templates ao dicionário
        self.templates[peticao_template.template_id] = peticao_template
        self.templates[contestacao_template.template_id] = contestacao_template
        self.templates[contrato_template.template_id] = contrato_template
    
    def get_template(self, template_id: str) -> Optional[DocumentTemplate]:
        """Obtém um template pelo ID."""
        return self.templates.get(template_id)
    
    def list_templates(self, document_type: Optional[DocumentType] = None, 
                      category: Optional[DocumentCategory] = None) -> List[DocumentTemplate]:
        """Lista templates, opcionalmente filtrados."""
        templates = list(self.templates.values())
        
        if document_type:
            templates = [t for t in templates if t.document_type == document_type]
        
        if category:
            templates = [t for t in templates if t.category == category]
        
        return templates

class AIDocumentEnhancer:
    """Aprimorador de documentos usando IA."""
    
    def __init__(self):
        self.client = OpenAI()
    
    def enhance_legal_text(self, text: str, document_type: DocumentType) -> str:
        """Aprimora texto jurídico usando IA."""
        try:
            prompt = f"""
            Você é um especialista em redação jurídica. Aprimore o seguinte texto para um documento do tipo "{document_type.value}":
            
            TEXTO ORIGINAL:
            {text}
            
            INSTRUÇÕES:
            1. Mantenha a estrutura e informações factuais
            2. Melhore a linguagem jurídica e técnica
            3. Corrija eventuais erros gramaticais
            4. Torne o texto mais claro e persuasivo
            5. Adicione fundamentação jurídica quando apropriado
            6. Mantenha o tom formal e respeitoso
            
            Retorne apenas o texto aprimorado, sem comentários adicionais.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=2000
            )
            
            enhanced_text = response.choices[0].message.content.strip()
            logger.info("Texto aprimorado com IA")
            return enhanced_text
            
        except Exception as e:
            logger.error(f"Erro ao aprimorar texto com IA: {e}")
            return text  # Retorna texto original em caso de erro
    
    def generate_legal_arguments(self, case_facts: str, legal_area: str) -> List[str]:
        """Gera argumentos jurídicos baseados nos fatos do caso."""
        try:
            prompt = f"""
            Com base nos fatos apresentados, gere argumentos jurídicos sólidos para a área do direito especificada.
            
            FATOS DO CASO:
            {case_facts}
            
            ÁREA DO DIREITO: {legal_area}
            
            Gere 3-5 argumentos jurídicos fundamentados, incluindo:
            1. Base legal (leis, súmulas, jurisprudência)
            2. Doutrina aplicável
            3. Precedentes relevantes
            
            Formato de resposta: Lista de argumentos separados por "|||"
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4,
                max_tokens=1500
            )
            
            arguments_text = response.choices[0].message.content.strip()
            arguments = [arg.strip() for arg in arguments_text.split("|||") if arg.strip()]
            
            logger.info(f"Gerados {len(arguments)} argumentos jurídicos")
            return arguments
            
        except Exception as e:
            logger.error(f"Erro ao gerar argumentos jurídicos: {e}")
            return ["Argumentos jurídicos não puderam ser gerados automaticamente."]

class DocumentGenerator:
    """Gerador principal de documentos jurídicos."""
    
    def __init__(self):
        self.template_manager = DocumentTemplateManager()
        self.ai_enhancer = AIDocumentEnhancer()
        self.generated_documents: Dict[str, GeneratedDocument] = {}
    
    def generate_document(self, template_id: str, document_data: DocumentData, 
                         enhance_with_ai: bool = True, generated_by: str = "Sistema") -> GeneratedDocument:
        """Gera um documento a partir de um template e dados."""
        template = self.template_manager.get_template(template_id)
        if not template:
            raise ValueError(f"Template {template_id} não encontrado")
        
        # Verificar campos obrigatórios
        missing_fields = []
        data_dict = asdict(document_data)
        
        for field in template.required_fields:
            if field not in data_dict or data_dict[field] is None:
                missing_fields.append(field)
        
        if missing_fields:
            raise ValueError(f"Campos obrigatórios ausentes: {', '.join(missing_fields)}")
        
        # Preparar dados para substituição
        replacement_data = self._prepare_replacement_data(document_data)
        
        # Substituir placeholders no template
        content = template.template_content
        for key, value in replacement_data.items():
            placeholder = "{" + key + "}"
            content = content.replace(placeholder, str(value))
        
        # Aprimorar com IA se solicitado
        if enhance_with_ai:
            content = self.ai_enhancer.enhance_legal_text(content, template.document_type)
        
        # Gerar título do documento
        title = self._generate_document_title(template, document_data)
        
        # Criar documento gerado
        document_id = str(uuid.uuid4())
        generated_doc = GeneratedDocument(
            document_id=document_id,
            template_id=template_id,
            document_type=template.document_type,
            title=title,
            content=content,
            data_used=document_data,
            generated_at=datetime.now(),
            generated_by=generated_by
        )
        
        self.generated_documents[document_id] = generated_doc
        logger.info(f"Documento gerado: {title}")
        return generated_doc
    
    def _prepare_replacement_data(self, document_data: DocumentData) -> Dict[str, str]:
        """Prepara dados para substituição no template."""
        data_dict = asdict(document_data)
        replacement_data = {}
        
        for key, value in data_dict.items():
            if value is not None:
                if isinstance(value, list):
                    # Converter listas em texto formatado
                    if key == "pedidos":
                        formatted_list = "\n".join([f"{chr(97+i)}) {item};" for i, item in enumerate(value)])
                        replacement_data[key] = formatted_list
                    elif key == "fundamentos_juridicos":
                        formatted_list = "\n\n".join([f"{i+1}. {item}" for i, item in enumerate(value)])
                        replacement_data[key] = formatted_list
                    else:
                        replacement_data[key] = "; ".join(value)
                elif isinstance(value, date):
                    replacement_data[key] = value.strftime("%d de %B de %Y")
                elif isinstance(value, float):
                    replacement_data[key] = f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                else:
                    replacement_data[key] = str(value)
            else:
                replacement_data[key] = "[CAMPO NÃO PREENCHIDO]"
        
        # Campos derivados
        if document_data.reu_cpf_cnpj:
            if len(document_data.reu_cpf_cnpj.replace(".", "").replace("-", "").replace("/", "")) == 11:
                replacement_data["reu_tipo"] = "física"
            else:
                replacement_data["reu_tipo"] = "jurídica"
        
        return replacement_data
    
    def _generate_document_title(self, template: DocumentTemplate, document_data: DocumentData) -> str:
        """Gera título para o documento."""
        base_title = template.name
        
        if document_data.autor_nome and document_data.reu_nome:
            return f"{base_title} - {document_data.autor_nome} vs {document_data.reu_nome}"
        elif document_data.autor_nome:
            return f"{base_title} - {document_data.autor_nome}"
        else:
            return base_title
    
    def save_document_to_file(self, document_id: str, file_path: str):
        """Salva documento em arquivo."""
        document = self.generated_documents.get(document_id)
        if not document:
            raise ValueError(f"Documento {document_id} não encontrado")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(document.content)
        
        document.file_path = file_path
        logger.info(f"Documento salvo em: {file_path}")
    
    def generate_with_ai_assistance(self, document_type: DocumentType, case_facts: str, 
                                  legal_area: str, basic_data: DocumentData) -> GeneratedDocument:
        """Gera documento com assistência completa da IA."""
        # Gerar argumentos jurídicos
        arguments = self.ai_enhancer.generate_legal_arguments(case_facts, legal_area)
        
        # Adicionar argumentos aos dados
        basic_data.fundamentos_juridicos = arguments
        basic_data.fatos = case_facts
        
        # Encontrar template apropriado
        templates = self.template_manager.list_templates(document_type=document_type)
        if not templates:
            raise ValueError(f"Nenhum template encontrado para {document_type.value}")
        
        template_id = templates[0].template_id
        
        # Gerar documento
        return self.generate_document(template_id, basic_data, enhance_with_ai=True)
    
    def export_document_data(self, document_id: str, output_path: str):
        """Exporta dados do documento para JSON."""
        document = self.generated_documents.get(document_id)
        if not document:
            raise ValueError(f"Documento {document_id} não encontrado")
        
        # Converter para dicionário
        doc_dict = asdict(document)
        
        # Converter enums e datetime
        doc_dict['document_type'] = document.document_type.value
        doc_dict['generated_at'] = document.generated_at.isoformat()
        
        # Converter data_used
        data_dict = asdict(document.data_used)
        if data_dict['data_documento']:
            data_dict['data_documento'] = document.data_used.data_documento.isoformat()
        doc_dict['data_used'] = data_dict
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(doc_dict, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Dados do documento exportados para: {output_path}")

def main():
    """Função principal para demonstração."""
    generator = DocumentGenerator()
    
    print("=== GERADOR DE DOCUMENTOS JURÍDICOS ===")
    
    # Dados de exemplo para petição inicial
    peticao_data = DocumentData(
        autor_nome="Maria Silva Santos",
        autor_cpf_cnpj="123.456.789-00",
        autor_endereco="Rua das Flores, 123, Centro, São Paulo/SP",
        autor_profissao="comerciante",
        reu_nome="Banco Exemplo S.A.",
        reu_cpf_cnpj="12.345.678/0001-90",
        reu_endereco="Av. Paulista, 1000, São Paulo/SP",
        advogado_nome="Dr. João Advogado",
        advogado_oab="SP 123.456",
        advogado_endereco="Rua dos Advogados, 456, São Paulo/SP",
        vara="1ª Vara Cível Central",
        causa_pedir="Cobrança de valores indevidamente descontados",
        pedidos=[
            "A procedência total dos pedidos",
            "A condenação do réu ao pagamento de R$ 15.000,00",
            "A condenação do réu ao pagamento de custas e honorários"
        ],
        valor_causa=15000.00,
        fatos="A autora mantinha conta corrente junto ao banco réu e teve valores indevidamente descontados de sua conta, sem autorização ou justificativa.",
        fundamentos_juridicos=[
            "Código de Defesa do Consumidor, art. 6º, VIII",
            "Código Civil, art. 884 - enriquecimento sem causa"
        ],
        local="São Paulo",
        data_documento=date.today()
    )
    
    # Gerar petição inicial
    try:
        peticao = generator.generate_document(
            template_id="peticao_inicial_001",
            document_data=peticao_data,
            enhance_with_ai=False,  # Desabilitado devido a limitações da API
            generated_by="Demonstração"
        )
        
        print(f"\nPetição gerada: {peticao.title}")
        print(f"ID: {peticao.document_id}")
        
        # Salvar petição
        peticao_path = "/home/ubuntu/peticao_inicial_exemplo.txt"
        generator.save_document_to_file(peticao.document_id, peticao_path)
        
    except Exception as e:
        print(f"Erro ao gerar petição: {e}")
    
    # Dados para contrato
    contrato_data = DocumentData(
        autor_nome="Empresa Contratante Ltda",
        autor_profissao="empresa",
        autor_cpf_cnpj="11.222.333/0001-44",
        autor_endereco="Rua Comercial, 789, São Paulo/SP",
        reu_nome="João Prestador de Serviços",
        reu_cpf_cnpj="987.654.321-00",
        reu_endereco="Rua do Prestador, 321, São Paulo/SP",
        objeto_contrato="prestação de serviços de consultoria em tecnologia da informação",
        prazo_contrato="6 (seis) meses",
        valor_contrato=30000.00,
        forma_pagamento="6 parcelas mensais de R$ 5.000,00",
        local="São Paulo",
        data_documento=date.today()
    )
    
    # Gerar contrato
    try:
        contrato = generator.generate_document(
            template_id="contrato_prestacao_001",
            document_data=contrato_data,
            enhance_with_ai=False,
            generated_by="Demonstração"
        )
        
        print(f"\nContrato gerado: {contrato.title}")
        print(f"ID: {contrato.document_id}")
        
        # Salvar contrato
        contrato_path = "/home/ubuntu/contrato_exemplo.txt"
        generator.save_document_to_file(contrato.document_id, contrato_path)
        
        # Exportar dados
        dados_path = "/home/ubuntu/dados_contrato.json"
        generator.export_document_data(contrato.document_id, dados_path)
        
    except Exception as e:
        print(f"Erro ao gerar contrato: {e}")
    
    # Listar templates disponíveis
    templates = generator.template_manager.list_templates()
    print(f"\nTemplates disponíveis ({len(templates)}):")
    for template in templates:
        print(f"  - {template.name} ({template.document_type.value})")
        print(f"    Campos obrigatórios: {len(template.required_fields)}")
        print(f"    Categoria: {template.category.value}")
    
    print(f"\nDocumentos gerados: {len(generator.generated_documents)}")
    print("Arquivos salvos:")
    print("  - peticao_inicial_exemplo.txt")
    print("  - contrato_exemplo.txt")
    print("  - dados_contrato.json")

if __name__ == "__main__":
    main()

