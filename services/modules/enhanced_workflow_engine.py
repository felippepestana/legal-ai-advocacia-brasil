#!/usr/bin/env python3
"""
Automação de Workflows - Versão Melhorada
Implementa melhorias: integração com sistemas externos, mais templates pré-configurados
e algoritmos refinados para maior precisão
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import asyncio
import requests
from concurrent.futures import ThreadPoolExecutor
import time

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WorkflowStatus(Enum):
    """Status do workflow"""
    DRAFT = "Rascunho"
    ACTIVE = "Ativo"
    PAUSED = "Pausado"
    COMPLETED = "Concluído"
    FAILED = "Falhou"
    CANCELLED = "Cancelado"

class StepType(Enum):
    """Tipos de etapas do workflow"""
    DOCUMENT_ANALYSIS = "Análise de Documento"
    DOCUMENT_GENERATION = "Geração de Documento"
    EMAIL_NOTIFICATION = "Notificação por Email"
    DEADLINE_CREATION = "Criação de Prazo"
    CALENDAR_EVENT = "Evento de Calendário"
    SYSTEM_INTEGRATION = "Integração de Sistema"
    APPROVAL_REQUEST = "Solicitação de Aprovação"
    CONDITIONAL_BRANCH = "Ramificação Condicional"
    DATA_VALIDATION = "Validação de Dados"
    REPORT_GENERATION = "Geração de Relatório"
    WEBHOOK_CALL = "Chamada de Webhook"
    DELAY = "Atraso"

class TriggerType(Enum):
    """Tipos de gatilhos para workflows"""
    MANUAL = "Manual"
    DOCUMENT_UPLOAD = "Upload de Documento"
    DEADLINE_APPROACHING = "Prazo Próximo"
    EMAIL_RECEIVED = "Email Recebido"
    CALENDAR_EVENT = "Evento de Calendário"
    SYSTEM_EVENT = "Evento do Sistema"
    SCHEDULED = "Agendado"
    WEBHOOK = "Webhook"

@dataclass
class WorkflowStep:
    """Etapa do workflow"""
    id: str
    name: str
    type: StepType
    config: Dict[str, Any]
    next_steps: List[str]
    conditions: List[Dict[str, Any]]
    timeout_minutes: int = 60
    retry_count: int = 3
    required: bool = True

@dataclass
class WorkflowExecution:
    """Execução de workflow"""
    id: str
    workflow_id: str
    status: WorkflowStatus
    current_step: Optional[str]
    start_time: datetime
    end_time: Optional[datetime]
    context: Dict[str, Any]
    step_results: Dict[str, Any]
    error_log: List[str]

@dataclass
class Workflow:
    """Definição de workflow"""
    id: str
    name: str
    description: str
    trigger: TriggerType
    trigger_config: Dict[str, Any]
    steps: List[WorkflowStep]
    variables: Dict[str, Any]
    created_by: str
    created_at: datetime
    updated_at: datetime
    status: WorkflowStatus
    tags: List[str]

class SystemIntegration:
    """Classe para integração com sistemas externos"""
    
    def __init__(self):
        self.integrations = {
            "email": self._send_email,
            "calendar": self._create_calendar_event,
            "document_storage": self._store_document,
            "crm": self._update_crm,
            "accounting": self._create_invoice,
            "tribunal_api": self._query_tribunal,
            "oab_api": self._validate_oab
        }
    
    async def execute_integration(self, integration_type: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Executa integração com sistema externo"""
        if integration_type not in self.integrations:
            raise ValueError(f"Integração {integration_type} não suportada")
        
        try:
            result = await self.integrations[integration_type](config)
            return {"success": True, "result": result}
        except Exception as e:
            logger.error(f"Erro na integração {integration_type}: {e}")
            return {"success": False, "error": str(e)}
    
    async def _send_email(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Simula envio de email"""
        await asyncio.sleep(0.1)  # Simula latência
        return {
            "message_id": str(uuid.uuid4()),
            "to": config.get("to", ""),
            "subject": config.get("subject", ""),
            "sent_at": datetime.now().isoformat()
        }
    
    async def _create_calendar_event(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Simula criação de evento no calendário"""
        await asyncio.sleep(0.1)
        return {
            "event_id": str(uuid.uuid4()),
            "title": config.get("title", ""),
            "date": config.get("date", ""),
            "created_at": datetime.now().isoformat()
        }
    
    async def _store_document(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Simula armazenamento de documento"""
        await asyncio.sleep(0.1)
        return {
            "document_id": str(uuid.uuid4()),
            "filename": config.get("filename", ""),
            "storage_path": f"/documents/{uuid.uuid4()}",
            "stored_at": datetime.now().isoformat()
        }
    
    async def _update_crm(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Simula atualização no CRM"""
        await asyncio.sleep(0.1)
        return {
            "client_id": config.get("client_id", ""),
            "updated_fields": config.get("fields", {}),
            "updated_at": datetime.now().isoformat()
        }
    
    async def _create_invoice(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Simula criação de fatura"""
        await asyncio.sleep(0.1)
        return {
            "invoice_id": str(uuid.uuid4()),
            "amount": config.get("amount", 0),
            "client": config.get("client", ""),
            "created_at": datetime.now().isoformat()
        }
    
    async def _query_tribunal(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Simula consulta a API de tribunal"""
        await asyncio.sleep(0.2)  # APIs de tribunal são mais lentas
        return {
            "process_number": config.get("process_number", ""),
            "status": "Em andamento",
            "last_update": datetime.now().isoformat(),
            "movements": ["Distribuição", "Citação", "Contestação"]
        }
    
    async def _validate_oab(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Simula validação de OAB"""
        await asyncio.sleep(0.1)
        oab_number = config.get("oab_number", "")
        return {
            "oab_number": oab_number,
            "valid": len(oab_number) > 5,  # Validação simples
            "lawyer_name": "Advogado Exemplo" if len(oab_number) > 5 else None,
            "validated_at": datetime.now().isoformat()
        }

class WorkflowTemplateLibrary:
    """Biblioteca de templates pré-configurados"""
    
    def __init__(self):
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, Workflow]:
        """Carrega templates pré-configurados"""
        templates = {}
        
        # Template: Processo de Petição Inicial
        templates["peticao_inicial"] = self._create_peticao_inicial_template()
        
        # Template: Acompanhamento de Prazo
        templates["acompanhamento_prazo"] = self._create_prazo_template()
        
        # Template: Análise de Contrato
        templates["analise_contrato"] = self._create_contrato_template()
        
        # Template: Cobrança Judicial
        templates["cobranca_judicial"] = self._create_cobranca_template()
        
        # Template: Recurso de Apelação
        templates["recurso_apelacao"] = self._create_recurso_template()
        
        # Template: Audiência de Conciliação
        templates["audiencia_conciliacao"] = self._create_audiencia_template()
        
        return templates
    
    def _create_peticao_inicial_template(self) -> Workflow:
        """Template para processo de petição inicial"""
        steps = [
            WorkflowStep(
                id="analyze_case",
                name="Analisar Caso",
                type=StepType.DOCUMENT_ANALYSIS,
                config={"analysis_type": "case_analysis"},
                next_steps=["validate_documents"],
                conditions=[]
            ),
            WorkflowStep(
                id="validate_documents",
                name="Validar Documentos",
                type=StepType.DATA_VALIDATION,
                config={"required_docs": ["cpf", "rg", "comprovante_residencia"]},
                next_steps=["generate_petition"],
                conditions=[]
            ),
            WorkflowStep(
                id="generate_petition",
                name="Gerar Petição Inicial",
                type=StepType.DOCUMENT_GENERATION,
                config={"template": "peticao_inicial", "format": "pdf"},
                next_steps=["create_deadline"],
                conditions=[]
            ),
            WorkflowStep(
                id="create_deadline",
                name="Criar Prazo de Acompanhamento",
                type=StepType.DEADLINE_CREATION,
                config={"type": "protocolo", "days": 5},
                next_steps=["notify_client"],
                conditions=[]
            ),
            WorkflowStep(
                id="notify_client",
                name="Notificar Cliente",
                type=StepType.EMAIL_NOTIFICATION,
                config={"template": "peticao_protocolada"},
                next_steps=[],
                conditions=[]
            )
        ]
        
        return Workflow(
            id="template_peticao_inicial",
            name="Processo de Petição Inicial",
            description="Workflow completo para elaboração e protocolo de petição inicial",
            trigger=TriggerType.MANUAL,
            trigger_config={},
            steps=steps,
            variables={"client_id": "", "case_type": "", "value": 0},
            created_by="system",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            status=WorkflowStatus.DRAFT,
            tags=["petição", "inicial", "processo"]
        )
    
    def _create_prazo_template(self) -> Workflow:
        """Template para acompanhamento de prazo"""
        steps = [
            WorkflowStep(
                id="check_deadline",
                name="Verificar Prazo",
                type=StepType.SYSTEM_INTEGRATION,
                config={"integration": "tribunal_api", "action": "check_process"},
                next_steps=["evaluate_urgency"],
                conditions=[]
            ),
            WorkflowStep(
                id="evaluate_urgency",
                name="Avaliar Urgência",
                type=StepType.CONDITIONAL_BRANCH,
                config={"condition": "days_remaining <= 3"},
                next_steps=["urgent_notification", "regular_notification"],
                conditions=[
                    {"field": "days_remaining", "operator": "<=", "value": 3, "next_step": "urgent_notification"},
                    {"field": "days_remaining", "operator": ">", "value": 3, "next_step": "regular_notification"}
                ]
            ),
            WorkflowStep(
                id="urgent_notification",
                name="Notificação Urgente",
                type=StepType.EMAIL_NOTIFICATION,
                config={"template": "prazo_urgente", "priority": "high"},
                next_steps=["create_calendar_event"],
                conditions=[]
            ),
            WorkflowStep(
                id="regular_notification",
                name="Notificação Regular",
                type=StepType.EMAIL_NOTIFICATION,
                config={"template": "prazo_regular", "priority": "normal"},
                next_steps=["create_calendar_event"],
                conditions=[]
            ),
            WorkflowStep(
                id="create_calendar_event",
                name="Criar Evento no Calendário",
                type=StepType.CALENDAR_EVENT,
                config={"type": "deadline_reminder"},
                next_steps=[],
                conditions=[]
            )
        ]
        
        return Workflow(
            id="template_acompanhamento_prazo",
            name="Acompanhamento de Prazo",
            description="Workflow para monitoramento e notificação de prazos processuais",
            trigger=TriggerType.DEADLINE_APPROACHING,
            trigger_config={"days_before": 7},
            steps=steps,
            variables={"process_number": "", "deadline_type": ""},
            created_by="system",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            status=WorkflowStatus.DRAFT,
            tags=["prazo", "notificação", "calendário"]
        )
    
    def _create_contrato_template(self) -> Workflow:
        """Template para análise de contrato"""
        steps = [
            WorkflowStep(
                id="analyze_contract",
                name="Analisar Contrato",
                type=StepType.DOCUMENT_ANALYSIS,
                config={"analysis_type": "contract_review"},
                next_steps=["identify_risks"],
                conditions=[]
            ),
            WorkflowStep(
                id="identify_risks",
                name="Identificar Riscos",
                type=StepType.DATA_VALIDATION,
                config={"risk_categories": ["clausulas_abusivas", "prazos", "valores"]},
                next_steps=["generate_report"],
                conditions=[]
            ),
            WorkflowStep(
                id="generate_report",
                name="Gerar Relatório de Análise",
                type=StepType.REPORT_GENERATION,
                config={"template": "analise_contrato", "include_recommendations": True},
                next_steps=["request_approval"],
                conditions=[]
            ),
            WorkflowStep(
                id="request_approval",
                name="Solicitar Aprovação",
                type=StepType.APPROVAL_REQUEST,
                config={"approver_role": "senior_lawyer"},
                next_steps=["notify_client"],
                conditions=[]
            ),
            WorkflowStep(
                id="notify_client",
                name="Notificar Cliente",
                type=StepType.EMAIL_NOTIFICATION,
                config={"template": "analise_concluida", "attach_report": True},
                next_steps=[],
                conditions=[]
            )
        ]
        
        return Workflow(
            id="template_analise_contrato",
            name="Análise de Contrato",
            description="Workflow para análise completa de contratos e identificação de riscos",
            trigger=TriggerType.DOCUMENT_UPLOAD,
            trigger_config={"document_type": "contract"},
            steps=steps,
            variables={"contract_type": "", "client_id": ""},
            created_by="system",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            status=WorkflowStatus.DRAFT,
            tags=["contrato", "análise", "risco"]
        )
    
    def _create_cobranca_template(self) -> Workflow:
        """Template para cobrança judicial"""
        steps = [
            WorkflowStep(
                id="validate_debt",
                name="Validar Dívida",
                type=StepType.DATA_VALIDATION,
                config={"required_fields": ["debtor", "amount", "due_date", "contract"]},
                next_steps=["calculate_interest"],
                conditions=[]
            ),
            WorkflowStep(
                id="calculate_interest",
                name="Calcular Juros e Correção",
                type=StepType.SYSTEM_INTEGRATION,
                config={"integration": "accounting", "action": "calculate_debt"},
                next_steps=["generate_demand_letter"],
                conditions=[]
            ),
            WorkflowStep(
                id="generate_demand_letter",
                name="Gerar Notificação Extrajudicial",
                type=StepType.DOCUMENT_GENERATION,
                config={"template": "notificacao_extrajudicial"},
                next_steps=["send_notification"],
                conditions=[]
            ),
            WorkflowStep(
                id="send_notification",
                name="Enviar Notificação",
                type=StepType.EMAIL_NOTIFICATION,
                config={"template": "cobranca_extrajudicial"},
                next_steps=["wait_response"],
                conditions=[]
            ),
            WorkflowStep(
                id="wait_response",
                name="Aguardar Resposta",
                type=StepType.DELAY,
                config={"days": 15},
                next_steps=["check_payment"],
                conditions=[]
            ),
            WorkflowStep(
                id="check_payment",
                name="Verificar Pagamento",
                type=StepType.CONDITIONAL_BRANCH,
                config={"condition": "payment_received == false"},
                next_steps=["prepare_lawsuit", "close_case"],
                conditions=[
                    {"field": "payment_received", "operator": "==", "value": False, "next_step": "prepare_lawsuit"},
                    {"field": "payment_received", "operator": "==", "value": True, "next_step": "close_case"}
                ]
            ),
            WorkflowStep(
                id="prepare_lawsuit",
                name="Preparar Ação Judicial",
                type=StepType.DOCUMENT_GENERATION,
                config={"template": "peticao_cobranca"},
                next_steps=[],
                conditions=[]
            ),
            WorkflowStep(
                id="close_case",
                name="Encerrar Caso",
                type=StepType.SYSTEM_INTEGRATION,
                config={"integration": "crm", "action": "close_case"},
                next_steps=[],
                conditions=[]
            )
        ]
        
        return Workflow(
            id="template_cobranca_judicial",
            name="Cobrança Judicial",
            description="Workflow completo para processo de cobrança extrajudicial e judicial",
            trigger=TriggerType.MANUAL,
            trigger_config={},
            steps=steps,
            variables={"debtor_id": "", "debt_amount": 0, "contract_id": ""},
            created_by="system",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            status=WorkflowStatus.DRAFT,
            tags=["cobrança", "extrajudicial", "judicial"]
        )
    
    def _create_recurso_template(self) -> Workflow:
        """Template para recurso de apelação"""
        steps = [
            WorkflowStep(
                id="analyze_sentence",
                name="Analisar Sentença",
                type=StepType.DOCUMENT_ANALYSIS,
                config={"analysis_type": "sentence_review"},
                next_steps=["identify_appeal_grounds"],
                conditions=[]
            ),
            WorkflowStep(
                id="identify_appeal_grounds",
                name="Identificar Fundamentos do Recurso",
                type=StepType.DATA_VALIDATION,
                config={"grounds_types": ["error_of_law", "error_of_fact", "procedural_error"]},
                next_steps=["research_jurisprudence"],
                conditions=[]
            ),
            WorkflowStep(
                id="research_jurisprudence",
                name="Pesquisar Jurisprudência",
                type=StepType.SYSTEM_INTEGRATION,
                config={"integration": "tribunal_api", "action": "search_jurisprudence"},
                next_steps=["draft_appeal"],
                conditions=[]
            ),
            WorkflowStep(
                id="draft_appeal",
                name="Redigir Recurso",
                type=StepType.DOCUMENT_GENERATION,
                config={"template": "recurso_apelacao"},
                next_steps=["review_appeal"],
                conditions=[]
            ),
            WorkflowStep(
                id="review_appeal",
                name="Revisar Recurso",
                type=StepType.APPROVAL_REQUEST,
                config={"approver_role": "senior_lawyer", "review_type": "appeal"},
                next_steps=["file_appeal"],
                conditions=[]
            ),
            WorkflowStep(
                id="file_appeal",
                name="Protocolar Recurso",
                type=StepType.SYSTEM_INTEGRATION,
                config={"integration": "tribunal_api", "action": "file_document"},
                next_steps=["create_follow_up"],
                conditions=[]
            ),
            WorkflowStep(
                id="create_follow_up",
                name="Criar Acompanhamento",
                type=StepType.DEADLINE_CREATION,
                config={"type": "recurso_julgamento", "days": 90},
                next_steps=[],
                conditions=[]
            )
        ]
        
        return Workflow(
            id="template_recurso_apelacao",
            name="Recurso de Apelação",
            description="Workflow para elaboração e protocolo de recurso de apelação",
            trigger=TriggerType.MANUAL,
            trigger_config={},
            steps=steps,
            variables={"process_number": "", "sentence_date": "", "appeal_deadline": ""},
            created_by="system",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            status=WorkflowStatus.DRAFT,
            tags=["recurso", "apelação", "tribunal"]
        )
    
    def _create_audiencia_template(self) -> Workflow:
        """Template para audiência de conciliação"""
        steps = [
            WorkflowStep(
                id="prepare_case_summary",
                name="Preparar Resumo do Caso",
                type=StepType.DOCUMENT_GENERATION,
                config={"template": "resumo_caso_audiencia"},
                next_steps=["research_settlement_precedents"],
                conditions=[]
            ),
            WorkflowStep(
                id="research_settlement_precedents",
                name="Pesquisar Precedentes de Acordo",
                type=StepType.SYSTEM_INTEGRATION,
                config={"integration": "tribunal_api", "action": "search_settlements"},
                next_steps=["calculate_settlement_range"],
                conditions=[]
            ),
            WorkflowStep(
                id="calculate_settlement_range",
                name="Calcular Faixa de Acordo",
                type=StepType.DATA_VALIDATION,
                config={"calculation_type": "settlement_range"},
                next_steps=["prepare_negotiation_strategy"],
                conditions=[]
            ),
            WorkflowStep(
                id="prepare_negotiation_strategy",
                name="Preparar Estratégia de Negociação",
                type=StepType.DOCUMENT_GENERATION,
                config={"template": "estrategia_negociacao"},
                next_steps=["schedule_client_meeting"],
                conditions=[]
            ),
            WorkflowStep(
                id="schedule_client_meeting",
                name="Agendar Reunião com Cliente",
                type=StepType.CALENDAR_EVENT,
                config={"type": "client_meeting", "duration": 60},
                next_steps=["send_hearing_reminder"],
                conditions=[]
            ),
            WorkflowStep(
                id="send_hearing_reminder",
                name="Enviar Lembrete da Audiência",
                type=StepType.EMAIL_NOTIFICATION,
                config={"template": "lembrete_audiencia", "days_before": 1},
                next_steps=["create_post_hearing_follow_up"],
                conditions=[]
            ),
            WorkflowStep(
                id="create_post_hearing_follow_up",
                name="Criar Acompanhamento Pós-Audiência",
                type=StepType.DEADLINE_CREATION,
                config={"type": "pos_audiencia", "days": 1},
                next_steps=[],
                conditions=[]
            )
        ]
        
        return Workflow(
            id="template_audiencia_conciliacao",
            name="Audiência de Conciliação",
            description="Workflow para preparação e acompanhamento de audiência de conciliação",
            trigger=TriggerType.CALENDAR_EVENT,
            trigger_config={"event_type": "hearing", "days_before": 7},
            steps=steps,
            variables={"process_number": "", "hearing_date": "", "client_id": ""},
            created_by="system",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            status=WorkflowStatus.DRAFT,
            tags=["audiência", "conciliação", "acordo"]
        )
    
    def get_template(self, template_id: str) -> Optional[Workflow]:
        """Retorna um template específico"""
        return self.templates.get(template_id)
    
    def list_templates(self) -> List[Dict[str, str]]:
        """Lista todos os templates disponíveis"""
        return [
            {
                "id": template_id,
                "name": workflow.name,
                "description": workflow.description,
                "tags": ", ".join(workflow.tags)
            }
            for template_id, workflow in self.templates.items()
        ]

class EnhancedWorkflowEngine:
    """Motor de workflow aprimorado com todas as melhorias"""
    
    def __init__(self):
        self.workflows: Dict[str, Workflow] = {}
        self.executions: Dict[str, WorkflowExecution] = {}
        self.integration = SystemIntegration()
        self.template_library = WorkflowTemplateLibrary()
        self.executor = ThreadPoolExecutor(max_workers=5)
    
    def create_workflow_from_template(self, template_id: str, name: str, variables: Dict[str, Any]) -> str:
        """Cria workflow a partir de template"""
        template = self.template_library.get_template(template_id)
        if not template:
            raise ValueError(f"Template {template_id} não encontrado")
        
        workflow_id = str(uuid.uuid4())
        workflow = Workflow(
            id=workflow_id,
            name=name,
            description=template.description,
            trigger=template.trigger,
            trigger_config=template.trigger_config,
            steps=template.steps.copy(),
            variables={**template.variables, **variables},
            created_by="user",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            status=WorkflowStatus.DRAFT,
            tags=template.tags.copy()
        )
        
        self.workflows[workflow_id] = workflow
        logger.info(f"Workflow criado a partir do template {template_id}: {workflow_id}")
        
        return workflow_id
    
    def create_custom_workflow(self, name: str, description: str, steps: List[WorkflowStep], 
                             trigger: TriggerType, variables: Dict[str, Any]) -> str:
        """Cria workflow personalizado"""
        workflow_id = str(uuid.uuid4())
        workflow = Workflow(
            id=workflow_id,
            name=name,
            description=description,
            trigger=trigger,
            trigger_config={},
            steps=steps,
            variables=variables,
            created_by="user",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            status=WorkflowStatus.DRAFT,
            tags=[]
        )
        
        self.workflows[workflow_id] = workflow
        logger.info(f"Workflow personalizado criado: {workflow_id}")
        
        return workflow_id
    
    async def execute_workflow(self, workflow_id: str, context: Dict[str, Any] = None) -> str:
        """Executa workflow de forma assíncrona"""
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow {workflow_id} não encontrado")
        
        workflow = self.workflows[workflow_id]
        execution_id = str(uuid.uuid4())
        
        execution = WorkflowExecution(
            id=execution_id,
            workflow_id=workflow_id,
            status=WorkflowStatus.ACTIVE,
            current_step=workflow.steps[0].id if workflow.steps else None,
            start_time=datetime.now(),
            end_time=None,
            context=context or {},
            step_results={},
            error_log=[]
        )
        
        self.executions[execution_id] = execution
        
        logger.info(f"Iniciando execução do workflow {workflow_id}: {execution_id}")
        
        # Executa workflow em background
        asyncio.create_task(self._execute_workflow_steps(execution_id))
        
        return execution_id
    
    async def _execute_workflow_steps(self, execution_id: str):
        """Executa as etapas do workflow"""
        execution = self.executions[execution_id]
        workflow = self.workflows[execution.workflow_id]
        
        try:
            current_step_id = execution.current_step
            
            while current_step_id:
                step = next((s for s in workflow.steps if s.id == current_step_id), None)
                if not step:
                    break
                
                logger.info(f"Executando etapa {step.name} do workflow {execution.workflow_id}")
                
                # Executa a etapa
                step_result = await self._execute_step(step, execution.context)
                execution.step_results[step.id] = step_result
                
                # Determina próxima etapa
                next_step_id = self._determine_next_step(step, step_result, execution.context)
                execution.current_step = next_step_id
                current_step_id = next_step_id
                
                # Pequena pausa entre etapas
                await asyncio.sleep(0.1)
            
            # Workflow concluído
            execution.status = WorkflowStatus.COMPLETED
            execution.end_time = datetime.now()
            
            logger.info(f"Workflow {execution.workflow_id} concluído com sucesso")
            
        except Exception as e:
            execution.status = WorkflowStatus.FAILED
            execution.end_time = datetime.now()
            execution.error_log.append(f"Erro na execução: {str(e)}")
            
            logger.error(f"Erro na execução do workflow {execution.workflow_id}: {e}")
    
    async def _execute_step(self, step: WorkflowStep, context: Dict[str, Any]) -> Dict[str, Any]:
        """Executa uma etapa específica"""
        start_time = time.time()
        
        try:
            if step.type == StepType.DOCUMENT_ANALYSIS:
                result = await self._execute_document_analysis(step.config, context)
            elif step.type == StepType.DOCUMENT_GENERATION:
                result = await self._execute_document_generation(step.config, context)
            elif step.type == StepType.EMAIL_NOTIFICATION:
                result = await self._execute_email_notification(step.config, context)
            elif step.type == StepType.SYSTEM_INTEGRATION:
                integration_type = step.config.get("integration")
                result = await self.integration.execute_integration(integration_type, step.config)
            elif step.type == StepType.DELAY:
                await asyncio.sleep(step.config.get("seconds", 1))
                result = {"delayed": True, "duration": step.config.get("seconds", 1)}
            elif step.type == StepType.CONDITIONAL_BRANCH:
                result = await self._execute_conditional_branch(step.config, context)
            else:
                result = {"message": f"Etapa {step.type.value} executada com sucesso"}
            
            execution_time = time.time() - start_time
            result["execution_time"] = execution_time
            result["success"] = True
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            return {
                "success": False,
                "error": str(e),
                "execution_time": execution_time
            }
    
    async def _execute_document_analysis(self, config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Executa análise de documento"""
        await asyncio.sleep(0.2)  # Simula processamento
        return {
            "analysis_type": config.get("analysis_type", "general"),
            "entities_found": 15,
            "concepts_identified": 8,
            "confidence": 0.92
        }
    
    async def _execute_document_generation(self, config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Executa geração de documento"""
        await asyncio.sleep(0.3)  # Simula geração
        return {
            "document_id": str(uuid.uuid4()),
            "template": config.get("template", "default"),
            "format": config.get("format", "pdf"),
            "pages": 3,
            "generated_at": datetime.now().isoformat()
        }
    
    async def _execute_email_notification(self, config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Executa notificação por email"""
        return await self.integration.execute_integration("email", config)
    
    async def _execute_conditional_branch(self, config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Executa ramificação condicional"""
        condition = config.get("condition", "true")
        # Simula avaliação da condição
        condition_result = True  # Simplificado
        
        return {
            "condition": condition,
            "result": condition_result,
            "branch_taken": "true_branch" if condition_result else "false_branch"
        }
    
    def _determine_next_step(self, step: WorkflowStep, step_result: Dict[str, Any], context: Dict[str, Any]) -> Optional[str]:
        """Determina a próxima etapa baseada no resultado"""
        if not step.next_steps:
            return None
        
        # Se há condições, avalia elas
        if step.conditions:
            for condition in step.conditions:
                if self._evaluate_condition(condition, step_result, context):
                    return condition.get("next_step")
        
        # Retorna primeira etapa da lista
        return step.next_steps[0] if step.next_steps else None
    
    def _evaluate_condition(self, condition: Dict[str, Any], step_result: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Avalia uma condição"""
        field = condition.get("field")
        operator = condition.get("operator")
        value = condition.get("value")
        
        # Busca valor no resultado da etapa ou contexto
        actual_value = step_result.get(field) or context.get(field)
        
        if operator == "==":
            return actual_value == value
        elif operator == "!=":
            return actual_value != value
        elif operator == ">":
            return actual_value > value
        elif operator == "<":
            return actual_value < value
        elif operator == ">=":
            return actual_value >= value
        elif operator == "<=":
            return actual_value <= value
        
        return False
    
    def get_execution_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Retorna status da execução"""
        if execution_id not in self.executions:
            return None
        
        execution = self.executions[execution_id]
        return {
            "id": execution.id,
            "workflow_id": execution.workflow_id,
            "status": execution.status.value,
            "current_step": execution.current_step,
            "start_time": execution.start_time.isoformat(),
            "end_time": execution.end_time.isoformat() if execution.end_time else None,
            "steps_completed": len(execution.step_results),
            "errors": execution.error_log
        }
    
    def list_workflows(self) -> List[Dict[str, Any]]:
        """Lista todos os workflows"""
        return [
            {
                "id": workflow.id,
                "name": workflow.name,
                "description": workflow.description,
                "status": workflow.status.value,
                "created_at": workflow.created_at.isoformat(),
                "steps_count": len(workflow.steps),
                "tags": workflow.tags
            }
            for workflow in self.workflows.values()
        ]
    
    def get_workflow_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas dos workflows"""
        total_workflows = len(self.workflows)
        total_executions = len(self.executions)
        
        if total_executions == 0:
            return {
                "total_workflows": total_workflows,
                "total_executions": 0,
                "success_rate": 0,
                "average_execution_time": 0
            }
        
        successful_executions = sum(1 for e in self.executions.values() if e.status == WorkflowStatus.COMPLETED)
        success_rate = (successful_executions / total_executions) * 100
        
        completed_executions = [e for e in self.executions.values() if e.end_time]
        if completed_executions:
            avg_time = sum((e.end_time - e.start_time).total_seconds() for e in completed_executions) / len(completed_executions)
        else:
            avg_time = 0
        
        return {
            "total_workflows": total_workflows,
            "total_executions": total_executions,
            "successful_executions": successful_executions,
            "success_rate": round(success_rate, 2),
            "average_execution_time": round(avg_time, 2)
        }

async def main():
    """Função principal para demonstração"""
    print("=== Automação de Workflows - Versão Melhorada ===")
    
    # Cria instância do motor de workflow
    engine = EnhancedWorkflowEngine()
    
    # Lista templates disponíveis
    templates = engine.template_library.list_templates()
    print(f"\nTemplates disponíveis ({len(templates)}):")
    for template in templates:
        print(f"- {template['name']}: {template['description']}")
    
    # Cria workflow a partir de template
    workflow_id = engine.create_workflow_from_template(
        "peticao_inicial",
        "Petição Inicial - Cliente João Silva",
        {
            "client_id": "12345",
            "case_type": "Danos Morais",
            "value": 20000.00
        }
    )
    
    print(f"\nWorkflow criado: {workflow_id}")
    
    # Executa workflow
    execution_id = await engine.execute_workflow(workflow_id, {"urgency": "normal"})
    print(f"Execução iniciada: {execution_id}")
    
    # Aguarda um pouco para a execução
    await asyncio.sleep(2)
    
    # Verifica status
    status = engine.get_execution_status(execution_id)
    if status:
        print(f"\nStatus da execução:")
        print(f"- Status: {status['status']}")
        print(f"- Etapas concluídas: {status['steps_completed']}")
        print(f"- Erros: {len(status['errors'])}")
    
    # Estatísticas
    stats = engine.get_workflow_statistics()
    print(f"\nEstatísticas:")
    print(f"- Total de workflows: {stats['total_workflows']}")
    print(f"- Total de execuções: {stats['total_executions']}")
    print(f"- Taxa de sucesso: {stats['success_rate']}%")
    print(f"- Tempo médio de execução: {stats['average_execution_time']}s")
    
    return engine

if __name__ == "__main__":
    asyncio.run(main())

