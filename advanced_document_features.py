"""
Funcionalidades Avançadas de Geração de Documentos
Implementa novos templates, personalização avançada e validação automática
"""

import json
import re
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import openai
import time

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentComplexity(Enum):
    """Níveis de complexidade de documentos"""
    SIMPLE = "Simples"
    INTERMEDIATE = "Intermediário"
    COMPLEX = "Complexo"
    EXPERT = "Especializado"

class ValidationLevel(Enum):
    """Níveis de validação de documentos"""
    BASIC = "Básico"
    STANDARD = "Padrão"
    COMPREHENSIVE = "Abrangente"
    EXPERT = "Especialista"

@dataclass
class DocumentValidationResult:
    """Resultado da validação de documento"""
    is_valid: bool
    score: float
    issues: List[Dict[str, Any]]
    suggestions: List[str]
    compliance_check: Dict[str, bool]
    readability_score: float

@dataclass
class AdvancedTemplate:
    """Template avançado de documento"""
    id: str
    name: str
    description: str
    category: str
    complexity: DocumentComplexity
    required_fields: List[str]
    optional_fields: List[str]
    validation_rules: List[Dict[str, Any]]
    ai_enhancement_prompts: Dict[str, str]
    template_content: str
    metadata: Dict[str, Any]

class AdvancedDocumentValidator:
    """Validador avançado de documentos jurídicos"""
    
    def __init__(self):
        self.validation_rules = self._load_validation_rules()
        self.legal_requirements = self._load_legal_requirements()
        
    def _load_validation_rules(self) -> Dict[str, List[Dict[str, Any]]]:
        """Carrega regras de validação por tipo de documento"""
        return {
            "peticao_inicial": [
                {
                    "rule": "required_parties",
                    "description": "Deve conter identificação completa das partes",
                    "pattern": r"(autor|requerente|impetrante).*?(réu|requerido|impetrado)",
                    "severity": "critical"
                },
                {
                    "rule": "legal_basis",
                    "description": "Deve conter fundamentação legal",
                    "pattern": r"(artigo|art\.|lei|código|constituição)",
                    "severity": "high"
                },
                {
                    "rule": "pedido_claro",
                    "description": "Deve conter pedido específico",
                    "pattern": r"(requer|pede|solicita|pleiteia)",
                    "severity": "critical"
                }
            ],
            "contrato": [
                {
                    "rule": "clausulas_essenciais",
                    "description": "Deve conter cláusulas essenciais",
                    "pattern": r"(cláusula|objeto|prazo|valor|rescisão)",
                    "severity": "critical"
                },
                {
                    "rule": "identificacao_partes",
                    "description": "Identificação completa das partes contratantes",
                    "pattern": r"(contratante|contratado|cpf|cnpj)",
                    "severity": "critical"
                }
            ],
            "recurso": [
                {
                    "rule": "fundamentacao_recursal",
                    "description": "Deve conter fundamentação específica do recurso",
                    "pattern": r"(apelação|agravo|embargos|recurso)",
                    "severity": "critical"
                },
                {
                    "rule": "prazo_recursal",
                    "description": "Deve mencionar observância do prazo",
                    "pattern": r"(prazo|tempestiv|intempestiv)",
                    "severity": "high"
                }
            ]
        }
    
    def _load_legal_requirements(self) -> Dict[str, Dict[str, Any]]:
        """Carrega requisitos legais por tipo de documento"""
        return {
            "peticao_inicial": {
                "cpc_requirements": [
                    "Juízo a que é dirigida",
                    "Nomes, prenomes, estado civil, existência de união estável, profissão, número de inscrição no CPF ou no CNPJ, endereço eletrônico, domicílio e residência do autor e do réu",
                    "Fato e os fundamentos jurídicos do pedido",
                    "Pedido com as suas especificações",
                    "Valor da causa",
                    "Provas com que o autor pretende demonstrar a verdade dos fatos alegados",
                    "Opção do autor pela realização ou não de audiência de conciliação ou de mediação"
                ],
                "formal_requirements": [
                    "Assinatura do advogado",
                    "Número da OAB",
                    "Data e local"
                ]
            },
            "contrato": {
                "essential_elements": [
                    "Identificação das partes",
                    "Objeto do contrato",
                    "Preço ou forma de pagamento",
                    "Prazo de vigência",
                    "Condições de rescisão"
                ],
                "recommended_clauses": [
                    "Cláusula de foro",
                    "Cláusula de multa",
                    "Cláusula de confidencialidade",
                    "Cláusula de força maior"
                ]
            }
        }
    
    def validate_document(self, content: str, document_type: str, 
                         validation_level: ValidationLevel = ValidationLevel.STANDARD) -> DocumentValidationResult:
        """Valida um documento jurídico"""
        issues = []
        suggestions = []
        compliance_check = {}
        
        # Validação básica de estrutura
        structure_score = self._validate_structure(content, document_type)
        
        # Validação de conteúdo
        content_score = self._validate_content(content, document_type, issues, suggestions)
        
        # Validação de conformidade legal
        legal_score = self._validate_legal_compliance(content, document_type, compliance_check)
        
        # Cálculo de legibilidade
        readability_score = self._calculate_readability(content)
        
        # Score geral
        overall_score = (structure_score + content_score + legal_score + readability_score) / 4
        
        # Determina se é válido
        is_valid = overall_score >= 0.7 and len([i for i in issues if i['severity'] == 'critical']) == 0
        
        return DocumentValidationResult(
            is_valid=is_valid,
            score=overall_score,
            issues=issues,
            suggestions=suggestions,
            compliance_check=compliance_check,
            readability_score=readability_score
        )
    
    def _validate_structure(self, content: str, document_type: str) -> float:
        """Valida a estrutura do documento"""
        score = 0.0
        
        # Verifica presença de elementos estruturais básicos
        if re.search(r'^[A-Z\s]+$', content.split('\n')[0]):  # Título em maiúsculas
            score += 0.2
        
        if len(content.split('\n')) >= 10:  # Documento com estrutura mínima
            score += 0.2
        
        if re.search(r'\d+\.\s', content):  # Numeração de itens
            score += 0.2
        
        if re.search(r'(Excelentíssimo|Meritíssimo|Ilustríssimo)', content):  # Tratamento formal
            score += 0.2
        
        if re.search(r'(Respeitosamente|Atenciosamente)', content):  # Fechamento formal
            score += 0.2
        
        return min(score, 1.0)
    
    def _validate_content(self, content: str, document_type: str, 
                         issues: List[Dict[str, Any]], suggestions: List[str]) -> float:
        """Valida o conteúdo específico do documento"""
        score = 1.0
        rules = self.validation_rules.get(document_type, [])
        
        for rule in rules:
            if not re.search(rule['pattern'], content, re.IGNORECASE):
                severity = rule['severity']
                issues.append({
                    'rule': rule['rule'],
                    'description': rule['description'],
                    'severity': severity,
                    'suggestion': f"Adicionar {rule['description'].lower()}"
                })
                
                # Penaliza o score baseado na severidade
                penalty = 0.3 if severity == 'critical' else 0.1 if severity == 'high' else 0.05
                score -= penalty
                
                suggestions.append(f"Incluir {rule['description'].lower()}")
        
        return max(score, 0.0)
    
    def _validate_legal_compliance(self, content: str, document_type: str, 
                                  compliance_check: Dict[str, bool]) -> float:
        """Valida conformidade com requisitos legais"""
        requirements = self.legal_requirements.get(document_type, {})
        total_requirements = 0
        met_requirements = 0
        
        for req_type, req_list in requirements.items():
            for requirement in req_list:
                total_requirements += 1
                # Simplificada: verifica se há palavras-chave relacionadas
                keywords = requirement.lower().split()
                if any(keyword in content.lower() for keyword in keywords[:3]):
                    met_requirements += 1
                    compliance_check[requirement] = True
                else:
                    compliance_check[requirement] = False
        
        return met_requirements / total_requirements if total_requirements > 0 else 1.0
    
    def _calculate_readability(self, content: str) -> float:
        """Calcula score de legibilidade"""
        # Implementação simplificada do índice de legibilidade
        sentences = len(re.findall(r'[.!?]+', content))
        words = len(content.split())
        
        if sentences == 0 or words == 0:
            return 0.0
        
        avg_sentence_length = words / sentences
        
        # Score baseado no comprimento médio das sentenças
        # Sentenças ideais: 15-20 palavras
        if 15 <= avg_sentence_length <= 20:
            return 1.0
        elif 10 <= avg_sentence_length <= 25:
            return 0.8
        elif 8 <= avg_sentence_length <= 30:
            return 0.6
        else:
            return 0.4

class AdvancedTemplateLibrary:
    """Biblioteca avançada de templates"""
    
    def __init__(self):
        self.templates = self._load_advanced_templates()
    
    def _load_advanced_templates(self) -> Dict[str, AdvancedTemplate]:
        """Carrega templates avançados"""
        templates = {}
        
        # Template de Ação de Cobrança Avançada
        templates["acao_cobranca_avancada"] = AdvancedTemplate(
            id="acao_cobranca_avancada",
            name="Ação de Cobrança - Modelo Avançado",
            description="Template avançado para ação de cobrança com cálculos automáticos",
            category="Cível",
            complexity=DocumentComplexity.INTERMEDIATE,
            required_fields=["autor_nome", "reu_nome", "valor_principal", "data_vencimento"],
            optional_fields=["juros", "multa", "correcao_monetaria", "honorarios"],
            validation_rules=[
                {"field": "valor_principal", "type": "currency", "min": 0},
                {"field": "data_vencimento", "type": "date", "max_age_days": 3650}
            ],
            ai_enhancement_prompts={
                "legal_basis": "Elabore fundamentação jurídica sólida para cobrança de dívida vencida",
                "calculation": "Calcule juros, multa e correção monetária até a data atual"
            },
            template_content=self._get_acao_cobranca_template(),
            metadata={"version": "2.0", "last_updated": "2025-09-14"}
        )
        
        # Template de Contrato de Prestação de Serviços Avançado
        templates["contrato_servicos_avancado"] = AdvancedTemplate(
            id="contrato_servicos_avancado",
            name="Contrato de Prestação de Serviços - Modelo Avançado",
            description="Template completo com cláusulas de proteção e compliance",
            category="Empresarial",
            complexity=DocumentComplexity.COMPLEX,
            required_fields=["contratante", "contratado", "objeto", "valor", "prazo"],
            optional_fields=["garantias", "penalidades", "confidencialidade", "propriedade_intelectual"],
            validation_rules=[
                {"field": "valor", "type": "currency", "min": 0},
                {"field": "prazo", "type": "integer", "min": 1, "max": 120}
            ],
            ai_enhancement_prompts={
                "risk_analysis": "Analise riscos contratuais e sugira cláusulas de proteção",
                "compliance": "Verifique conformidade com legislação trabalhista e tributária"
            },
            template_content=self._get_contrato_servicos_template(),
            metadata={"version": "2.0", "last_updated": "2025-09-14"}
        )
        
        # Template de Recurso de Apelação Avançado
        templates["recurso_apelacao_avancado"] = AdvancedTemplate(
            id="recurso_apelacao_avancado",
            name="Recurso de Apelação - Modelo Avançado",
            description="Template com análise jurisprudencial automática",
            category="Processual",
            complexity=DocumentComplexity.EXPERT,
            required_fields=["apelante", "apelado", "sentenca_data", "fundamentos"],
            optional_fields=["jurisprudencia", "doutrina", "pedido_liminar"],
            validation_rules=[
                {"field": "sentenca_data", "type": "date", "max_age_days": 15}
            ],
            ai_enhancement_prompts={
                "jurisprudence": "Busque jurisprudência relevante e precedentes aplicáveis",
                "legal_analysis": "Analise os fundamentos da sentença e identifique pontos de recurso"
            },
            template_content=self._get_recurso_apelacao_template(),
            metadata={"version": "2.0", "last_updated": "2025-09-14"}
        )
        
        return templates
    
    def _get_acao_cobranca_template(self) -> str:
        """Template de ação de cobrança avançada"""
        return """
EXCELENTÍSSIMO SENHOR DOUTOR JUIZ DE DIREITO DA {vara} VARA CÍVEL DA COMARCA DE {comarca}

{autor_nome}, {autor_qualificacao}, vem, respeitosamente, perante Vossa Excelência, por meio de seu advogado que esta subscreve, propor a presente

AÇÃO DE COBRANÇA

em face de {reu_nome}, {reu_qualificacao}, pelos fatos e fundamentos jurídicos a seguir expostos:

I - DOS FATOS

{fatos_narrativa}

O valor principal da dívida é de R$ {valor_principal}, vencido em {data_vencimento}.

II - DOS CÁLCULOS ATUALIZADOS

Valor principal: R$ {valor_principal}
Correção monetária (IPCA): R$ {correcao_monetaria}
Juros de mora ({taxa_juros}% a.m.): R$ {juros_mora}
Multa contratual ({percentual_multa}%): R$ {multa}
Honorários advocatícios: R$ {honorarios}

TOTAL ATUALIZADO: R$ {valor_total}

III - DO DIREITO

{fundamentacao_juridica}

IV - DOS PEDIDOS

Ante o exposto, requer:

a) A citação do réu para, querendo, contestar a presente ação no prazo legal;
b) A procedência total da ação, condenando o réu ao pagamento da quantia de R$ {valor_total};
c) A condenação do réu ao pagamento das custas processuais e honorários advocatícios;
d) Protesta por todos os meios de prova em direito admitidos.

Dá-se à causa o valor de R$ {valor_causa}.

{local}, {data}.

{advogado_nome}
OAB/{estado} {numero_oab}
"""
    
    def _get_contrato_servicos_template(self) -> str:
        """Template de contrato de serviços avançado"""
        return """
CONTRATO DE PRESTAÇÃO DE SERVIÇOS

CONTRATANTE: {contratante_nome}, {contratante_qualificacao}
CONTRATADO: {contratado_nome}, {contratado_qualificacao}

CLÁUSULA 1ª - DO OBJETO
{objeto_detalhado}

CLÁUSULA 2ª - DO VALOR E FORMA DE PAGAMENTO
O valor total dos serviços é de R$ {valor_total}, a ser pago {forma_pagamento}.

CLÁUSULA 3ª - DO PRAZO
O prazo para execução dos serviços é de {prazo_execucao}, iniciando-se em {data_inicio}.

CLÁUSULA 4ª - DAS OBRIGAÇÕES DO CONTRATANTE
{obrigacoes_contratante}

CLÁUSULA 5ª - DAS OBRIGAÇÕES DO CONTRATADO
{obrigacoes_contratado}

CLÁUSULA 6ª - DA CONFIDENCIALIDADE
{clausula_confidencialidade}

CLÁUSULA 7ª - DA PROPRIEDADE INTELECTUAL
{clausula_propriedade_intelectual}

CLÁUSULA 8ª - DAS PENALIDADES
{clausula_penalidades}

CLÁUSULA 9ª - DA RESCISÃO
{clausula_rescisao}

CLÁUSULA 10ª - DO FORO
Fica eleito o foro de {foro_eleito} para dirimir quaisquer controvérsias.

{local}, {data}.

_________________________        _________________________
{contratante_nome}               {contratado_nome}

Testemunhas:
1. _________________________
2. _________________________
"""
    
    def _get_recurso_apelacao_template(self) -> str:
        """Template de recurso de apelação avançado"""
        return """
EXCELENTÍSSIMO SENHOR DESEMBARGADOR RELATOR DO TRIBUNAL DE JUSTIÇA DE {estado}

{apelante_nome}, {apelante_qualificacao}, vem, respeitosamente, por meio de seu advogado que esta subscreve, interpor

RECURSO DE APELAÇÃO

da r. sentença proferida nos autos do processo nº {numero_processo}, em trâmite perante a {vara_origem}, pelos fundamentos que passa a expor:

I - DA TEMPESTIVIDADE
O presente recurso é tempestivo, tendo sido a sentença publicada em {data_publicacao}.

II - DO PREPARO
O preparo foi devidamente recolhido, conforme comprovantes anexos.

III - DOS FUNDAMENTOS DO RECURSO

{fundamentos_recurso}

IV - DA JURISPRUDÊNCIA

{jurisprudencia_aplicavel}

V - DOS PEDIDOS

Ante o exposto, requer:

a) O conhecimento e provimento do presente recurso;
b) A reforma da r. sentença recorrida;
c) {pedidos_especificos}

{local}, {data}.

{advogado_nome}
OAB/{estado} {numero_oab}
"""

class AdvancedDocumentGenerator:
    """Gerador avançado de documentos jurídicos"""
    
    def __init__(self):
        self.template_library = AdvancedTemplateLibrary()
        self.validator = AdvancedDocumentValidator()
        self.ai_enhancer = self._initialize_ai_enhancer()
    
    def _initialize_ai_enhancer(self):
        """Inicializa o sistema de melhoria por IA"""
        return {
            "client": openai.OpenAI(),
            "model": "gpt-4.1-mini",
            "max_tokens": 2000
        }
    
    def generate_advanced_document(self, template_id: str, data: Dict[str, Any], 
                                 options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Gera documento com funcionalidades avançadas"""
        options = options or {}
        
        # Obtém template
        template = self.template_library.templates.get(template_id)
        if not template:
            raise ValueError(f"Template {template_id} não encontrado")
        
        # Valida dados de entrada
        validation_errors = self._validate_input_data(data, template)
        if validation_errors:
            return {"error": "Dados inválidos", "details": validation_errors}
        
        # Processa dados
        processed_data = self._process_data_with_calculations(data, template)
        
        # Gera conteúdo base
        base_content = self._generate_base_content(template, processed_data)
        
        # Aplica melhorias de IA se solicitado
        if options.get("ai_enhancement", True):
            enhanced_content = self._apply_ai_enhancements(base_content, template, processed_data)
        else:
            enhanced_content = base_content
        
        # Valida documento gerado
        validation_level_str = options.get("validation_level", "STANDARD")
        if validation_level_str == "COMPREHENSIVE":
            validation_level = ValidationLevel.COMPREHENSIVE
        elif validation_level_str == "EXPERT":
            validation_level = ValidationLevel.EXPERT
        elif validation_level_str == "BASIC":
            validation_level = ValidationLevel.BASIC
        else:
            validation_level = ValidationLevel.STANDARD
            
        validation_result = self.validator.validate_document(
            enhanced_content, 
            template_id,
            validation_level
        )
        
        # Aplica formatação final
        final_content = self._apply_final_formatting(enhanced_content, options)
        
        return {
            "content": final_content,
            "template_used": template_id,
            "validation": asdict(validation_result),
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "complexity": template.complexity.value,
                "word_count": len(final_content.split()),
                "ai_enhanced": options.get("ai_enhancement", True)
            }
        }
    
    def _validate_input_data(self, data: Dict[str, Any], template: AdvancedTemplate) -> List[str]:
        """Valida dados de entrada"""
        errors = []
        
        # Verifica campos obrigatórios
        for field in template.required_fields:
            if field not in data or not data[field]:
                errors.append(f"Campo obrigatório '{field}' não fornecido")
        
        # Aplica regras de validação específicas
        for rule in template.validation_rules:
            field = rule["field"]
            if field in data:
                if not self._validate_field(data[field], rule):
                    errors.append(f"Campo '{field}' não atende aos critérios: {rule}")
        
        return errors
    
    def _validate_field(self, value: Any, rule: Dict[str, Any]) -> bool:
        """Valida um campo específico"""
        field_type = rule.get("type")
        
        if field_type == "currency":
            try:
                float_value = float(str(value).replace(",", "."))
                return float_value >= rule.get("min", 0)
            except:
                return False
        
        elif field_type == "date":
            try:
                date_obj = datetime.strptime(str(value), "%Y-%m-%d")
                max_age = rule.get("max_age_days")
                if max_age:
                    return (datetime.now() - date_obj).days <= max_age
                return True
            except:
                return False
        
        elif field_type == "integer":
            try:
                int_value = int(value)
                return (rule.get("min", float('-inf')) <= int_value <= 
                       rule.get("max", float('inf')))
            except:
                return False
        
        return True
    
    def _process_data_with_calculations(self, data: Dict[str, Any], template: AdvancedTemplate) -> Dict[str, Any]:
        """Processa dados com cálculos automáticos"""
        processed = data.copy()
        
        # Cálculos específicos para ação de cobrança
        if template.id == "acao_cobranca_avancada":
            processed.update(self._calculate_debt_values(data))
        
        # Adiciona data atual se não fornecida
        if "data" not in processed:
            processed["data"] = datetime.now().strftime("%d de %B de %Y")
        
        # Adiciona local se não fornecido
        if "local" not in processed:
            processed["local"] = "São Paulo"
        
        return processed
    
    def _calculate_debt_values(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula valores de dívida com juros e correção"""
        calculations = {}
        
        valor_principal = float(str(data.get("valor_principal", 0)).replace(",", "."))
        data_vencimento = datetime.strptime(data.get("data_vencimento", "2024-01-01"), "%Y-%m-%d")
        
        # Calcula dias em atraso
        dias_atraso = (datetime.now() - data_vencimento).days
        
        # Taxa de juros (padrão 1% ao mês)
        taxa_juros = float(data.get("taxa_juros", 1.0))
        
        # Correção monetária (IPCA estimado 0.5% ao mês)
        taxa_correcao = float(data.get("taxa_correcao", 0.5))
        
        # Cálculos
        meses_atraso = dias_atraso / 30
        
        correcao_monetaria = valor_principal * (taxa_correcao / 100) * meses_atraso
        juros_mora = valor_principal * (taxa_juros / 100) * meses_atraso
        
        # Multa (padrão 2%)
        percentual_multa = float(data.get("percentual_multa", 2.0))
        multa = valor_principal * (percentual_multa / 100)
        
        # Honorários (padrão 20%)
        percentual_honorarios = float(data.get("percentual_honorarios", 20.0))
        honorarios = valor_principal * (percentual_honorarios / 100)
        
        valor_total = valor_principal + correcao_monetaria + juros_mora + multa + honorarios
        
        calculations.update({
            "correcao_monetaria": f"{correcao_monetaria:.2f}",
            "juros_mora": f"{juros_mora:.2f}",
            "multa": f"{multa:.2f}",
            "honorarios": f"{honorarios:.2f}",
            "valor_total": f"{valor_total:.2f}",
            "valor_causa": f"{valor_total:.2f}",
            "dias_atraso": dias_atraso,
            "taxa_juros": taxa_juros,
            "percentual_multa": percentual_multa
        })
        
        return calculations
    
    def _generate_base_content(self, template: AdvancedTemplate, data: Dict[str, Any]) -> str:
        """Gera conteúdo base do documento"""
        content = template.template_content
        
        # Substitui placeholders
        for key, value in data.items():
            placeholder = "{" + key + "}"
            content = content.replace(placeholder, str(value))
        
        return content
    
    def _apply_ai_enhancements(self, content: str, template: AdvancedTemplate, data: Dict[str, Any]) -> str:
        """Aplica melhorias usando IA"""
        enhanced_content = content
        
        try:
            for enhancement_type, prompt in template.ai_enhancement_prompts.items():
                if enhancement_type in ["legal_basis", "fundamentacao_juridica"]:
                    enhanced_section = self._generate_legal_basis(data, prompt)
                    enhanced_content = enhanced_content.replace("{fundamentacao_juridica}", enhanced_section)
                
                elif enhancement_type == "jurisprudence":
                    jurisprudence_section = self._generate_jurisprudence_section(data)
                    enhanced_content = enhanced_content.replace("{jurisprudencia_aplicavel}", jurisprudence_section)
        
        except Exception as e:
            logger.warning(f"Erro na melhoria por IA: {e}")
        
        return enhanced_content
    
    def _generate_legal_basis(self, data: Dict[str, Any], prompt: str) -> str:
        """Gera fundamentação jurídica usando IA"""
        try:
            response = self.ai_enhancer["client"].chat.completions.create(
                model=self.ai_enhancer["model"],
                messages=[
                    {"role": "system", "content": "Você é um especialista em direito brasileiro. Elabore fundamentação jurídica precisa e bem estruturada."},
                    {"role": "user", "content": f"{prompt}. Contexto: {json.dumps(data, ensure_ascii=False)}"}
                ],
                max_tokens=self.ai_enhancer["max_tokens"]
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            logger.error(f"Erro na geração de fundamentação jurídica: {e}")
            return "A fundamentação jurídica será elaborada conforme a legislação aplicável ao caso."
    
    def _generate_jurisprudence_section(self, data: Dict[str, Any]) -> str:
        """Gera seção de jurisprudência"""
        # Implementação simplificada - em produção, integraria com base de jurisprudência
        return """
Neste sentido, colaciona-se jurisprudência do Superior Tribunal de Justiça:

"PROCESSUAL CIVIL. RECURSO ESPECIAL. (...) A jurisprudência desta Corte é pacífica no sentido de que (...)"
(STJ, REsp nº 1.234.567/SP, Rel. Min. Fulano de Tal, 3ª Turma, julgado em 01/01/2024)

Ademais, o Tribunal de Justiça tem decidido:

"(...) Precedente aplicável ao caso em tela (...)"
(TJSP, Apelação nº 1234567-89.2024.8.26.0100, Rel. Des. Sicrano, 1ª Câmara de Direito Privado, julgado em 01/01/2024)
"""
    
    def _apply_final_formatting(self, content: str, options: Dict[str, Any]) -> str:
        """Aplica formatação final ao documento"""
        formatted = content
        
        # Remove linhas em branco excessivas
        formatted = re.sub(r'\n\s*\n\s*\n', '\n\n', formatted)
        
        # Ajusta espaçamento
        formatted = formatted.strip()
        
        # Aplica formatação específica se solicitada
        if options.get("format") == "pdf_ready":
            formatted = self._format_for_pdf(formatted)
        
        return formatted
    
    def _format_for_pdf(self, content: str) -> str:
        """Formata para geração de PDF"""
        # Adiciona quebras de página onde necessário
        content = content.replace("IV - DOS PEDIDOS", "\n\nIV - DOS PEDIDOS")
        
        # Ajusta margens e espaçamento
        lines = content.split('\n')
        formatted_lines = []
        
        for line in lines:
            if line.strip().isupper() and len(line.strip()) > 10:
                # Títulos principais
                formatted_lines.append(f"\n{line.strip()}\n")
            else:
                formatted_lines.append(line)
        
        return '\n'.join(formatted_lines)

def main():
    """Função principal para demonstração"""
    print("=== Funcionalidades Avançadas de Geração de Documentos ===")
    
    # Cria instância do gerador avançado
    generator = AdvancedDocumentGenerator()
    
    # Lista templates disponíveis
    templates = list(generator.template_library.templates.keys())
    print(f"\nTemplates avançados disponíveis ({len(templates)}):")
    for template_id in templates:
        template = generator.template_library.templates[template_id]
        print(f"- {template.name} ({template.complexity.value})")
    
    # Dados de exemplo para ação de cobrança
    dados_cobranca = {
        "vara": "1ª",
        "comarca": "São Paulo",
        "autor_nome": "JOÃO SILVA",
        "autor_qualificacao": "brasileiro, casado, empresário, CPF 123.456.789-10",
        "reu_nome": "EMPRESA XYZ LTDA",
        "reu_qualificacao": "pessoa jurídica de direito privado, CNPJ 12.345.678/0001-90",
        "valor_principal": "15000.00",
        "data_vencimento": "2023-06-15",
        "fatos_narrativa": "O autor prestou serviços de consultoria ao réu, conforme contrato anexo, sendo que o pagamento não foi efetuado na data acordada.",
        "advogado_nome": "Dr. Carlos Santos",
        "estado": "SP",
        "numero_oab": "123456"
    }
    
    # Gera documento avançado
    print(f"\nGerando ação de cobrança avançada...")
    resultado = generator.generate_advanced_document(
        "acao_cobranca_avancada", 
        dados_cobranca,
        {
            "ai_enhancement": True,
            "validation_level": "COMPREHENSIVE",
            "format": "pdf_ready"
        }
    )
    
    if "error" not in resultado:
        print(f"Documento gerado com sucesso!")
        print(f"Complexidade: {resultado['metadata']['complexity']}")
        print(f"Palavras: {resultado['metadata']['word_count']}")
        print(f"Score de validação: {resultado['validation']['score']:.2f}")
        print(f"Documento válido: {resultado['validation']['is_valid']}")
        
        if resultado['validation']['issues']:
            print(f"Problemas encontrados: {len(resultado['validation']['issues'])}")
        
        # Salva documento
        with open("/home/ubuntu/documento_avancado_exemplo.txt", "w", encoding="utf-8") as f:
            f.write(resultado['content'])
        
        print("Documento salvo em: documento_avancado_exemplo.txt")
    else:
        print(f"Erro na geração: {resultado['error']}")
    
    return generator

if __name__ == "__main__":
    main()

