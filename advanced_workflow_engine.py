#!/usr/bin/env python3
"""
Motor Avançado de Automação de Workflows Jurídicos
Sistema completo de automação com suporte a workflows complexos, condicionais e integração com IA.
"""

import os
import json
import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, asdict, field
from enum import Enum
from abc import ABC, abstractmethod
import threading
import time
from concurrent.futures import ThreadPoolExecutor, Future

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TriggerType(Enum):
    MANUAL_TRIGGER = "manual"
    DOCUMENT_UPLOAD = "document_upload"
    DEADLINE_APPROACHING = "deadline_approaching"
    EMAIL_RECEIVED = "email_received"
    CALENDAR_EVENT = "calendar_event"
    PROCESS_UPDATE = "process_update"
    SCHEDULED_TIME = "scheduled_time"
    WEBHOOK = "webhook"
    FILE_CHANGE = "file_change"

class ActionType(Enum):
    SEND_EMAIL = "send_email"
    SEND_NOTIFICATION = "send_notification"
    CREATE_TASK = "create_task"
    ANALYZE_DOCUMENT = "analyze_document"
    GENERATE_DOCUMENT = "generate_document"
    UPDATE_CALENDAR = "update_calendar"
    SEND_WEBHOOK = "send_webhook"
    EXECUTE_SCRIPT = "execute_script"
    CONDITIONAL_BRANCH = "conditional_branch"
    DELAY = "delay"
    APPROVE_WORKFLOW = "approve_workflow"

class WorkflowStatus(Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ExecutionStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    WAITING_APPROVAL = "waiting_approval"

@dataclass
class WorkflowTrigger:
    type: TriggerType
    conditions: Dict[str, Any]
    description: str
    enabled: bool = True

@dataclass
class WorkflowAction:
    type: ActionType
    parameters: Dict[str, Any]
    description: str
    timeout: int = 300  # 5 minutos por padrão
    retry_count: int = 3
    on_failure: Optional[str] = None  # ID da ação a executar em caso de falha
    conditions: Optional[Dict[str, Any]] = None  # Condições para execução

@dataclass
class WorkflowExecution:
    execution_id: str
    workflow_id: str
    status: ExecutionStatus
    trigger_data: Dict[str, Any]
    actions_executed: List[str]
    current_action: Optional[str]
    start_time: datetime
    end_time: Optional[datetime]
    error_message: Optional[str]
    execution_log: List[str] = field(default_factory=list)
    context_data: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Workflow:
    workflow_id: str
    name: str
    description: str
    triggers: List[WorkflowTrigger]
    actions: List[WorkflowAction]
    status: WorkflowStatus
    created_by: str
    created_at: datetime
    updated_at: datetime
    tags: List[str] = field(default_factory=list)
    priority: int = 5  # 1-10, onde 10 é mais alta
    max_concurrent_executions: int = 1
    timeout: int = 3600  # 1 hora por padrão

class ActionExecutor(ABC):
    """Classe base para executores de ação."""
    
    @abstractmethod
    def execute(self, action: WorkflowAction, context: Dict[str, Any]) -> Dict[str, Any]:
        """Executa uma ação e retorna o resultado."""
        pass
    
    @abstractmethod
    def can_handle(self, action_type: ActionType) -> bool:
        """Verifica se pode executar o tipo de ação."""
        pass

class EmailActionExecutor(ActionExecutor):
    """Executor para ações de envio de email."""
    
    def can_handle(self, action_type: ActionType) -> bool:
        return action_type == ActionType.SEND_EMAIL
    
    def execute(self, action: WorkflowAction, context: Dict[str, Any]) -> Dict[str, Any]:
        to = action.parameters.get('to')
        subject = action.parameters.get('subject', 'Notificação do Sistema Jurídico')
        body = action.parameters.get('body', '')
        
        # Substituir variáveis do contexto no corpo do email
        for key, value in context.items():
            body = body.replace(f'{{{key}}}', str(value))
        
        logger.info(f"Email enviado para {to}: {subject}")
        
        return {
            'status': 'success',
            'message': f'Email enviado para {to}',
            'timestamp': datetime.now().isoformat()
        }

class NotificationActionExecutor(ActionExecutor):
    """Executor para ações de notificação."""
    
    def can_handle(self, action_type: ActionType) -> bool:
        return action_type == ActionType.SEND_NOTIFICATION
    
    def execute(self, action: WorkflowAction, context: Dict[str, Any]) -> Dict[str, Any]:
        title = action.parameters.get('title', 'Notificação')
        message = action.parameters.get('message', '')
        recipient = action.parameters.get('recipient')
        
        logger.info(f"Notificação enviada: {title} para {recipient}")
        
        return {
            'status': 'success',
            'notification_id': str(uuid.uuid4()),
            'timestamp': datetime.now().isoformat()
        }

class TaskActionExecutor(ActionExecutor):
    """Executor para ações de criação de tarefas."""
    
    def can_handle(self, action_type: ActionType) -> bool:
        return action_type == ActionType.CREATE_TASK
    
    def execute(self, action: WorkflowAction, context: Dict[str, Any]) -> Dict[str, Any]:
        title = action.parameters.get('title', 'Nova Tarefa')
        description = action.parameters.get('description', '')
        assignee = action.parameters.get('assignee')
        due_date = action.parameters.get('due_date')
        priority = action.parameters.get('priority', 'medium')
        
        task_id = str(uuid.uuid4())
        
        logger.info(f"Tarefa criada: {title} para {assignee}")
        
        return {
            'status': 'success',
            'task_id': task_id,
            'title': title,
            'assignee': assignee,
            'timestamp': datetime.now().isoformat()
        }

class DocumentAnalysisActionExecutor(ActionExecutor):
    """Executor para ações de análise de documentos."""
    
    def can_handle(self, action_type: ActionType) -> bool:
        return action_type == ActionType.ANALYZE_DOCUMENT
    
    def execute(self, action: WorkflowAction, context: Dict[str, Any]) -> Dict[str, Any]:
        document_path = action.parameters.get('document_path')
        analysis_type = action.parameters.get('analysis_type', 'full')
        
        if not document_path:
            raise ValueError("document_path é obrigatório para análise de documento")
        
        # Simular análise de documento (integração com advanced_document_analyzer)
        logger.info(f"Analisando documento: {document_path}")
        
        # Aqui seria integrado com o AdvancedDocumentAnalyzer
        analysis_result = {
            'document_type': 'Petição Inicial',
            'entities_found': 5,
            'opportunities': 2,
            'confidence': 0.85,
            'processing_time': 2.3
        }
        
        return {
            'status': 'success',
            'analysis_result': analysis_result,
            'timestamp': datetime.now().isoformat()
        }

class ConditionalActionExecutor(ActionExecutor):
    """Executor para ações condicionais."""
    
    def can_handle(self, action_type: ActionType) -> bool:
        return action_type == ActionType.CONDITIONAL_BRANCH
    
    def execute(self, action: WorkflowAction, context: Dict[str, Any]) -> Dict[str, Any]:
        condition = action.parameters.get('condition')
        true_action = action.parameters.get('true_action')
        false_action = action.parameters.get('false_action')
        
        # Avaliar condição (implementação simplificada)
        result = self._evaluate_condition(condition, context)
        
        next_action = true_action if result else false_action
        
        logger.info(f"Condição avaliada: {condition} = {result}, próxima ação: {next_action}")
        
        return {
            'status': 'success',
            'condition_result': result,
            'next_action': next_action,
            'timestamp': datetime.now().isoformat()
        }
    
    def _evaluate_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """Avalia uma condição simples."""
        try:
            # Substituir variáveis do contexto
            for key, value in context.items():
                condition = condition.replace(f'{{{key}}}', str(value))
            
            # Avaliar expressão (cuidado com segurança em produção)
            return eval(condition)
        except Exception as e:
            logger.error(f"Erro ao avaliar condição {condition}: {e}")
            return False

class DelayActionExecutor(ActionExecutor):
    """Executor para ações de delay/espera."""
    
    def can_handle(self, action_type: ActionType) -> bool:
        return action_type == ActionType.DELAY
    
    def execute(self, action: WorkflowAction, context: Dict[str, Any]) -> Dict[str, Any]:
        delay_seconds = action.parameters.get('delay_seconds', 60)
        
        logger.info(f"Aguardando {delay_seconds} segundos...")
        time.sleep(delay_seconds)
        
        return {
            'status': 'success',
            'delay_seconds': delay_seconds,
            'timestamp': datetime.now().isoformat()
        }

class AdvancedWorkflowEngine:
    """Motor avançado de automação de workflows."""
    
    def __init__(self):
        self.workflows: Dict[str, Workflow] = {}
        self.executions: Dict[str, WorkflowExecution] = {}
        self.executors: List[ActionExecutor] = []
        self.executor_pool = ThreadPoolExecutor(max_workers=10)
        self.running_executions: Dict[str, Future] = {}
        
        # Registrar executores padrão
        self._register_default_executors()
        
        # Thread para monitoramento de execuções
        self.monitor_thread = threading.Thread(target=self._monitor_executions, daemon=True)
        self.monitor_thread.start()
    
    def _register_default_executors(self):
        """Registra os executores padrão."""
        self.executors.extend([
            EmailActionExecutor(),
            NotificationActionExecutor(),
            TaskActionExecutor(),
            DocumentAnalysisActionExecutor(),
            ConditionalActionExecutor(),
            DelayActionExecutor()
        ])
    
    def register_workflow(self, workflow: Workflow) -> str:
        """Registra um novo workflow."""
        self.workflows[workflow.workflow_id] = workflow
        logger.info(f"Workflow registrado: {workflow.name} ({workflow.workflow_id})")
        return workflow.workflow_id
    
    def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """Obtém um workflow pelo ID."""
        return self.workflows.get(workflow_id)
    
    def list_workflows(self, status: Optional[WorkflowStatus] = None) -> List[Workflow]:
        """Lista workflows, opcionalmente filtrados por status."""
        workflows = list(self.workflows.values())
        if status:
            workflows = [w for w in workflows if w.status == status]
        return workflows
    
    def trigger_workflow(self, workflow_id: str, trigger_data: Dict[str, Any]) -> str:
        """Dispara a execução de um workflow."""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} não encontrado")
        
        if workflow.status != WorkflowStatus.ACTIVE:
            raise ValueError(f"Workflow {workflow_id} não está ativo")
        
        # Verificar limite de execuções concorrentes
        active_executions = sum(1 for exec in self.executions.values() 
                              if exec.workflow_id == workflow_id and 
                              exec.status in [ExecutionStatus.PENDING, ExecutionStatus.RUNNING])
        
        if active_executions >= workflow.max_concurrent_executions:
            raise ValueError(f"Limite de execuções concorrentes atingido para workflow {workflow_id}")
        
        # Criar execução
        execution_id = str(uuid.uuid4())
        execution = WorkflowExecution(
            execution_id=execution_id,
            workflow_id=workflow_id,
            status=ExecutionStatus.PENDING,
            trigger_data=trigger_data,
            actions_executed=[],
            current_action=None,
            start_time=datetime.now(),
            end_time=None,
            error_message=None
        )
        
        self.executions[execution_id] = execution
        
        # Submeter para execução assíncrona
        future = self.executor_pool.submit(self._execute_workflow, execution_id)
        self.running_executions[execution_id] = future
        
        logger.info(f"Execução iniciada: {execution_id} para workflow {workflow_id}")
        return execution_id
    
    def _execute_workflow(self, execution_id: str):
        """Executa um workflow de forma assíncrona."""
        execution = self.executions[execution_id]
        workflow = self.workflows[execution.workflow_id]
        
        try:
            execution.status = ExecutionStatus.RUNNING
            execution.context_data.update(execution.trigger_data)
            
            logger.info(f"Iniciando execução do workflow: {workflow.name}")
            
            # Executar ações sequencialmente
            for i, action in enumerate(workflow.actions):
                execution.current_action = f"action_{i}"
                
                # Verificar condições da ação
                if action.conditions and not self._evaluate_action_conditions(action.conditions, execution.context_data):
                    logger.info(f"Pulando ação {action.description} - condições não atendidas")
                    continue
                
                # Executar ação
                try:
                    result = self._execute_action(action, execution.context_data)
                    execution.actions_executed.append(execution.current_action)
                    execution.execution_log.append(f"Ação executada: {action.description}")
                    
                    # Atualizar contexto com resultado
                    execution.context_data[f"action_{i}_result"] = result
                    
                    # Verificar se é uma ação condicional que altera o fluxo
                    if action.type == ActionType.CONDITIONAL_BRANCH:
                        next_action_id = result.get('next_action')
                        if next_action_id:
                            # Implementar lógica de salto para ação específica
                            logger.info(f"Saltando para ação: {next_action_id}")
                    
                except Exception as e:
                    logger.error(f"Erro na execução da ação {action.description}: {e}")
                    execution.execution_log.append(f"Erro na ação {action.description}: {str(e)}")
                    
                    # Tentar executar ação de falha se definida
                    if action.on_failure:
                        try:
                            failure_action = next((a for a in workflow.actions if a.description == action.on_failure), None)
                            if failure_action:
                                self._execute_action(failure_action, execution.context_data)
                        except Exception as fe:
                            logger.error(f"Erro na ação de falha: {fe}")
                    
                    # Decidir se continua ou para a execução
                    if action.retry_count > 0:
                        # Implementar lógica de retry
                        pass
                    else:
                        raise e
            
            execution.status = ExecutionStatus.COMPLETED
            execution.end_time = datetime.now()
            logger.info(f"Workflow {workflow.name} executado com sucesso")
            
        except Exception as e:
            execution.status = ExecutionStatus.FAILED
            execution.error_message = str(e)
            execution.end_time = datetime.now()
            logger.error(f"Falha na execução do workflow {workflow.name}: {e}")
        
        finally:
            execution.current_action = None
            if execution_id in self.running_executions:
                del self.running_executions[execution_id]
    
    def _execute_action(self, action: WorkflowAction, context: Dict[str, Any]) -> Dict[str, Any]:
        """Executa uma ação específica."""
        executor = next((e for e in self.executors if e.can_handle(action.type)), None)
        if not executor:
            raise ValueError(f"Nenhum executor encontrado para ação do tipo {action.type}")
        
        logger.info(f"Executando ação: {action.description}")
        return executor.execute(action, context)
    
    def _evaluate_action_conditions(self, conditions: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Avalia as condições de uma ação."""
        # Implementação simplificada
        for key, expected_value in conditions.items():
            if context.get(key) != expected_value:
                return False
        return True
    
    def _monitor_executions(self):
        """Monitora execuções em andamento para timeouts."""
        while True:
            try:
                current_time = datetime.now()
                
                for execution_id, execution in list(self.executions.items()):
                    if execution.status == ExecutionStatus.RUNNING:
                        workflow = self.workflows.get(execution.workflow_id)
                        if workflow and (current_time - execution.start_time).total_seconds() > workflow.timeout:
                            logger.warning(f"Timeout na execução {execution_id}")
                            execution.status = ExecutionStatus.FAILED
                            execution.error_message = "Timeout na execução"
                            execution.end_time = current_time
                            
                            # Cancelar future se ainda estiver rodando
                            if execution_id in self.running_executions:
                                future = self.running_executions[execution_id]
                                future.cancel()
                                del self.running_executions[execution_id]
                
                time.sleep(30)  # Verificar a cada 30 segundos
                
            except Exception as e:
                logger.error(f"Erro no monitoramento de execuções: {e}")
                time.sleep(60)
    
    def get_execution_status(self, execution_id: str) -> Optional[WorkflowExecution]:
        """Obtém o status de uma execução."""
        return self.executions.get(execution_id)
    
    def cancel_execution(self, execution_id: str) -> bool:
        """Cancela uma execução em andamento."""
        execution = self.executions.get(execution_id)
        if not execution:
            return False
        
        if execution.status in [ExecutionStatus.PENDING, ExecutionStatus.RUNNING]:
            execution.status = ExecutionStatus.CANCELLED
            execution.end_time = datetime.now()
            
            # Cancelar future se ainda estiver rodando
            if execution_id in self.running_executions:
                future = self.running_executions[execution_id]
                future.cancel()
                del self.running_executions[execution_id]
            
            logger.info(f"Execução {execution_id} cancelada")
            return True
        
        return False
    
    def export_workflow(self, workflow_id: str, file_path: str):
        """Exporta um workflow para arquivo JSON."""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} não encontrado")
        
        # Converter para dicionário
        workflow_dict = asdict(workflow)
        
        # Converter enums para strings
        workflow_dict['status'] = workflow.status.value
        workflow_dict['created_at'] = workflow.created_at.isoformat()
        workflow_dict['updated_at'] = workflow.updated_at.isoformat()
        
        for trigger in workflow_dict['triggers']:
            trigger['type'] = TriggerType(trigger['type']).value
        
        for action in workflow_dict['actions']:
            action['type'] = ActionType(action['type']).value
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(workflow_dict, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Workflow exportado para: {file_path}")

class AdvancedWorkflowBuilder:
    """Construtor avançado de workflows com suporte a funcionalidades complexas."""
    
    def __init__(self, name: str, description: str):
        self.workflow_id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.triggers: List[WorkflowTrigger] = []
        self.actions: List[WorkflowAction] = []
        self.tags: List[str] = []
        self.priority = 5
        self.max_concurrent_executions = 1
        self.timeout = 3600
    
    def add_trigger(self, trigger_type: TriggerType, conditions: Dict[str, Any], description: str) -> 'AdvancedWorkflowBuilder':
        """Adiciona um gatilho ao workflow."""
        trigger = WorkflowTrigger(
            type=trigger_type,
            conditions=conditions,
            description=description
        )
        self.triggers.append(trigger)
        return self
    
    def add_action(self, action_type: ActionType, parameters: Dict[str, Any], description: str, 
                   timeout: int = 300, retry_count: int = 3, on_failure: Optional[str] = None,
                   conditions: Optional[Dict[str, Any]] = None) -> 'AdvancedWorkflowBuilder':
        """Adiciona uma ação ao workflow."""
        action = WorkflowAction(
            type=action_type,
            parameters=parameters,
            description=description,
            timeout=timeout,
            retry_count=retry_count,
            on_failure=on_failure,
            conditions=conditions
        )
        self.actions.append(action)
        return self
    
    def add_conditional_branch(self, condition: str, true_action: str, false_action: str, 
                             description: str = "Ramificação condicional") -> 'AdvancedWorkflowBuilder':
        """Adiciona uma ramificação condicional ao workflow."""
        return self.add_action(
            ActionType.CONDITIONAL_BRANCH,
            {
                'condition': condition,
                'true_action': true_action,
                'false_action': false_action
            },
            description
        )
    
    def add_delay(self, delay_seconds: int, description: str = "Aguardar") -> 'AdvancedWorkflowBuilder':
        """Adiciona um delay ao workflow."""
        return self.add_action(
            ActionType.DELAY,
            {'delay_seconds': delay_seconds},
            f"{description} ({delay_seconds}s)"
        )
    
    def set_priority(self, priority: int) -> 'AdvancedWorkflowBuilder':
        """Define a prioridade do workflow (1-10)."""
        self.priority = max(1, min(10, priority))
        return self
    
    def set_concurrency_limit(self, max_executions: int) -> 'AdvancedWorkflowBuilder':
        """Define o limite de execuções concorrentes."""
        self.max_concurrent_executions = max(1, max_executions)
        return self
    
    def set_timeout(self, timeout_seconds: int) -> 'AdvancedWorkflowBuilder':
        """Define o timeout do workflow."""
        self.timeout = max(60, timeout_seconds)
        return self
    
    def add_tags(self, *tags: str) -> 'AdvancedWorkflowBuilder':
        """Adiciona tags ao workflow."""
        self.tags.extend(tags)
        return self
    
    def build(self, created_by: str) -> Workflow:
        """Constrói o workflow final."""
        return Workflow(
            workflow_id=self.workflow_id,
            name=self.name,
            description=self.description,
            triggers=self.triggers,
            actions=self.actions,
            status=WorkflowStatus.ACTIVE,
            created_by=created_by,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            tags=self.tags,
            priority=self.priority,
            max_concurrent_executions=self.max_concurrent_executions,
            timeout=self.timeout
        )

def main():
    """Função principal para demonstração."""
    engine = AdvancedWorkflowEngine()
    
    # Criar workflow complexo de exemplo
    workflow = (AdvancedWorkflowBuilder("Análise Automática de Petição", "Workflow para análise automática de petições recebidas")
                .add_trigger(TriggerType.DOCUMENT_UPLOAD, {'file_type': 'pdf'}, "Upload de documento PDF")
                .add_action(ActionType.ANALYZE_DOCUMENT, 
                           {'document_path': '{uploaded_file}', 'analysis_type': 'full'}, 
                           "Analisar documento com IA")
                .add_conditional_branch(
                    '{action_0_result.analysis_result.confidence} > 0.8',
                    'high_confidence_flow',
                    'low_confidence_flow',
                    "Verificar confiança da análise"
                )
                .add_action(ActionType.CREATE_TASK,
                           {'title': 'Revisar análise de documento', 
                            'description': 'Documento analisado com baixa confiança',
                            'assignee': 'advogado_senior',
                            'priority': 'high'},
                           "Criar tarefa para revisão manual",
                           conditions={'action_1_result.condition_result': False})
                .add_action(ActionType.SEND_EMAIL,
                           {'to': 'cliente@email.com',
                            'subject': 'Documento analisado com sucesso',
                            'body': 'Seu documento foi analisado. Tipo: {action_0_result.analysis_result.document_type}'},
                           "Notificar cliente sobre análise",
                           conditions={'action_1_result.condition_result': True})
                .add_delay(300, "Aguardar processamento")
                .add_action(ActionType.SEND_NOTIFICATION,
                           {'title': 'Workflow concluído',
                            'message': 'Análise de petição finalizada',
                            'recipient': 'sistema'},
                           "Notificação final")
                .set_priority(8)
                .set_concurrency_limit(3)
                .set_timeout(1800)
                .add_tags('analise', 'peticao', 'automatico')
                .build("admin"))
    
    # Registrar workflow
    workflow_id = engine.register_workflow(workflow)
    
    # Executar workflow
    execution_id = engine.trigger_workflow(workflow_id, {
        'uploaded_file': '/home/ubuntu/exemplo_sentenca_avancada.txt',
        'user_id': 'user123'
    })
    
    print(f"Workflow executado: {execution_id}")
    
    # Aguardar conclusão
    time.sleep(2)
    
    # Verificar status
    execution = engine.get_execution_status(execution_id)
    if execution:
        print(f"Status: {execution.status.value}")
        print(f"Ações executadas: {len(execution.actions_executed)}")
        print(f"Log de execução:")
        for log_entry in execution.execution_log:
            print(f"  - {log_entry}")
    
    # Exportar workflow
    engine.export_workflow(workflow_id, "/home/ubuntu/workflow_avancado_exemplo.json")
    print("Workflow exportado para workflow_avancado_exemplo.json")

if __name__ == "__main__":
    main()

