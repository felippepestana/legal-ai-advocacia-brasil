#!/usr/bin/env python3
"""
Sistema de Gestão Inteligente de Prazos Jurídicos
Monitora prazos processuais, calcula datas, envia alertas e sugere ações preventivas.
"""

import os
import json
import uuid
import logging
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import calendar

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DeadlineType(Enum):
    RECURSO = "recurso"
    CONTESTACAO = "contestacao"
    REPLICAS = "replicas"
    EMBARGOS = "embargos"
    CUMPRIMENTO_SENTENCA = "cumprimento_sentenca"
    MANIFESTACAO = "manifestacao"
    AUDIENCIA = "audiencia"
    PERICIA = "pericia"
    JUNTADA_DOCUMENTOS = "juntada_documentos"
    PAGAMENTO = "pagamento"
    CUSTOM = "custom"

class DeadlineStatus(Enum):
    ATIVO = "ativo"
    CUMPRIDO = "cumprido"
    PERDIDO = "perdido"
    CANCELADO = "cancelado"
    SUSPENSO = "suspenso"

class AlertType(Enum):
    CRITICO = "critico"  # 1-2 dias
    URGENTE = "urgente"  # 3-5 dias
    IMPORTANTE = "importante"  # 6-10 dias
    INFORMATIVO = "informativo"  # 11+ dias

class CourtType(Enum):
    ESTADUAL = "estadual"
    FEDERAL = "federal"
    TRABALHISTA = "trabalhista"
    ELEITORAL = "eleitoral"
    MILITAR = "militar"
    SUPERIOR = "superior"

@dataclass
class LegalDeadline:
    deadline_id: str
    process_number: str
    deadline_type: DeadlineType
    description: str
    due_date: date
    court_type: CourtType
    status: DeadlineStatus
    responsible_lawyer: str
    client_name: str
    created_at: datetime
    updated_at: datetime
    completion_date: Optional[date] = None
    notes: str = ""
    priority: int = 5  # 1-10
    estimated_hours: float = 0.0
    dependencies: List[str] = None  # IDs de outros prazos
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []

@dataclass
class DeadlineAlert:
    alert_id: str
    deadline_id: str
    alert_type: AlertType
    message: str
    scheduled_date: datetime
    sent_date: Optional[datetime]
    recipients: List[str]
    is_sent: bool = False

@dataclass
class DeadlineCalculation:
    calculation_id: str
    base_date: date
    deadline_type: DeadlineType
    court_type: CourtType
    calculated_date: date
    business_days: int
    excluded_dates: List[date]
    calculation_details: str

class BrazilianHolidayCalculator:
    """Calculadora de feriados brasileiros e dias úteis."""
    
    def __init__(self):
        # Feriados fixos nacionais
        self.fixed_holidays = {
            (1, 1): "Confraternização Universal",
            (4, 21): "Tiradentes",
            (5, 1): "Dia do Trabalhador",
            (9, 7): "Independência do Brasil",
            (10, 12): "Nossa Senhora Aparecida",
            (11, 2): "Finados",
            (11, 15): "Proclamação da República",
            (12, 25): "Natal"
        }
    
    def is_holiday(self, date_obj: date) -> bool:
        """Verifica se uma data é feriado."""
        # Feriados fixos
        if (date_obj.month, date_obj.day) in self.fixed_holidays:
            return True
        
        # Carnaval (47 dias antes da Páscoa)
        easter = self._calculate_easter(date_obj.year)
        carnival_monday = easter - timedelta(days=48)
        carnival_tuesday = easter - timedelta(days=47)
        
        if date_obj in [carnival_monday, carnival_tuesday]:
            return True
        
        # Sexta-feira Santa (2 dias antes da Páscoa)
        good_friday = easter - timedelta(days=2)
        if date_obj == good_friday:
            return True
        
        # Corpus Christi (60 dias após a Páscoa)
        corpus_christi = easter + timedelta(days=60)
        if date_obj == corpus_christi:
            return True
        
        return False
    
    def _calculate_easter(self, year: int) -> date:
        """Calcula a data da Páscoa para um ano específico."""
        # Algoritmo de Gauss para cálculo da Páscoa
        a = year % 19
        b = year // 100
        c = year % 100
        d = b // 4
        e = b % 4
        f = (b + 8) // 25
        g = (b - f + 1) // 3
        h = (19 * a + b - d - g + 15) % 30
        i = c // 4
        k = c % 4
        l = (32 + 2 * e + 2 * i - h - k) % 7
        m = (a + 11 * h + 22 * l) // 451
        month = (h + l - 7 * m + 114) // 31
        day = ((h + l - 7 * m + 114) % 31) + 1
        
        return date(year, month, day)
    
    def is_business_day(self, date_obj: date) -> bool:
        """Verifica se uma data é dia útil."""
        # Não é fim de semana e não é feriado
        return date_obj.weekday() < 5 and not self.is_holiday(date_obj)
    
    def add_business_days(self, start_date: date, business_days: int) -> date:
        """Adiciona dias úteis a uma data."""
        current_date = start_date
        days_added = 0
        
        while days_added < business_days:
            current_date += timedelta(days=1)
            if self.is_business_day(current_date):
                days_added += 1
        
        return current_date
    
    def count_business_days(self, start_date: date, end_date: date) -> int:
        """Conta dias úteis entre duas datas."""
        if start_date > end_date:
            return 0
        
        current_date = start_date
        business_days = 0
        
        while current_date <= end_date:
            if self.is_business_day(current_date):
                business_days += 1
            current_date += timedelta(days=1)
        
        return business_days

class DeadlineCalculator:
    """Calculadora de prazos jurídicos brasileiros."""
    
    def __init__(self):
        self.holiday_calculator = BrazilianHolidayCalculator()
        
        # Prazos padrão por tipo (em dias úteis)
        self.standard_deadlines = {
            DeadlineType.RECURSO: 15,
            DeadlineType.CONTESTACAO: 15,
            DeadlineType.REPLICAS: 10,
            DeadlineType.EMBARGOS: 15,
            DeadlineType.CUMPRIMENTO_SENTENCA: 15,
            DeadlineType.MANIFESTACAO: 15,
            DeadlineType.JUNTADA_DOCUMENTOS: 5,
            DeadlineType.PAGAMENTO: 15
        }
    
    def calculate_deadline(self, base_date: date, deadline_type: DeadlineType, 
                          court_type: CourtType, custom_days: Optional[int] = None) -> DeadlineCalculation:
        """Calcula um prazo jurídico."""
        calculation_id = str(uuid.uuid4())
        
        # Determinar número de dias
        if custom_days:
            business_days = custom_days
        else:
            business_days = self.standard_deadlines.get(deadline_type, 15)
        
        # Ajustes por tipo de tribunal
        if court_type == CourtType.TRABALHISTA:
            # Justiça do Trabalho tem prazos reduzidos
            business_days = max(5, business_days // 2)
        elif court_type == CourtType.SUPERIOR:
            # Tribunais superiores podem ter prazos diferenciados
            if deadline_type == DeadlineType.RECURSO:
                business_days = 15  # REsp e RE
        
        # Calcular data final
        calculated_date = self.holiday_calculator.add_business_days(base_date, business_days)
        
        # Identificar datas excluídas (feriados e fins de semana)
        excluded_dates = []
        current_date = base_date + timedelta(days=1)
        while current_date <= calculated_date:
            if not self.holiday_calculator.is_business_day(current_date):
                excluded_dates.append(current_date)
            current_date += timedelta(days=1)
        
        # Detalhes do cálculo
        details = f"Prazo de {business_days} dias úteis a partir de {base_date.strftime('%d/%m/%Y')} "
        details += f"({court_type.value}). Feriados/fins de semana excluídos: {len(excluded_dates)}"
        
        return DeadlineCalculation(
            calculation_id=calculation_id,
            base_date=base_date,
            deadline_type=deadline_type,
            court_type=court_type,
            calculated_date=calculated_date,
            business_days=business_days,
            excluded_dates=excluded_dates,
            calculation_details=details
        )

class DeadlineManager:
    """Gerenciador principal de prazos jurídicos."""
    
    def __init__(self):
        self.deadlines: Dict[str, LegalDeadline] = {}
        self.alerts: Dict[str, DeadlineAlert] = {}
        self.calculator = DeadlineCalculator()
        
        # Configurações de alerta (dias antes do vencimento)
        self.alert_thresholds = {
            AlertType.CRITICO: 2,
            AlertType.URGENTE: 5,
            AlertType.IMPORTANTE: 10,
            AlertType.INFORMATIVO: 15
        }
    
    def create_deadline(self, process_number: str, deadline_type: DeadlineType,
                       description: str, due_date: date, court_type: CourtType,
                       responsible_lawyer: str, client_name: str,
                       priority: int = 5, estimated_hours: float = 0.0,
                       notes: str = "") -> str:
        """Cria um novo prazo."""
        deadline_id = str(uuid.uuid4())
        
        deadline = LegalDeadline(
            deadline_id=deadline_id,
            process_number=process_number,
            deadline_type=deadline_type,
            description=description,
            due_date=due_date,
            court_type=court_type,
            status=DeadlineStatus.ATIVO,
            responsible_lawyer=responsible_lawyer,
            client_name=client_name,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            priority=priority,
            estimated_hours=estimated_hours,
            notes=notes
        )
        
        self.deadlines[deadline_id] = deadline
        
        # Criar alertas automáticos
        self._create_automatic_alerts(deadline)
        
        logger.info(f"Prazo criado: {description} - Vencimento: {due_date}")
        return deadline_id
    
    def _create_automatic_alerts(self, deadline: LegalDeadline):
        """Cria alertas automáticos para um prazo."""
        today = date.today()
        
        for alert_type, days_before in self.alert_thresholds.items():
            alert_date = deadline.due_date - timedelta(days=days_before)
            
            # Só criar alerta se a data ainda não passou
            if alert_date >= today:
                alert_id = str(uuid.uuid4())
                
                message = f"PRAZO {alert_type.value.upper()}: {deadline.description} "
                message += f"vence em {days_before} dias ({deadline.due_date.strftime('%d/%m/%Y')})"
                
                alert = DeadlineAlert(
                    alert_id=alert_id,
                    deadline_id=deadline.deadline_id,
                    alert_type=alert_type,
                    message=message,
                    scheduled_date=datetime.combine(alert_date, datetime.min.time().replace(hour=9)),
                    sent_date=None,
                    recipients=[deadline.responsible_lawyer]
                )
                
                self.alerts[alert_id] = alert
    
    def calculate_deadline_from_event(self, event_date: date, deadline_type: DeadlineType,
                                    court_type: CourtType, custom_days: Optional[int] = None) -> DeadlineCalculation:
        """Calcula um prazo a partir de um evento processual."""
        return self.calculator.calculate_deadline(event_date, deadline_type, court_type, custom_days)
    
    def get_pending_deadlines(self, lawyer: Optional[str] = None, 
                            days_ahead: int = 30) -> List[LegalDeadline]:
        """Obtém prazos pendentes."""
        today = date.today()
        cutoff_date = today + timedelta(days=days_ahead)
        
        pending = []
        for deadline in self.deadlines.values():
            if (deadline.status == DeadlineStatus.ATIVO and 
                deadline.due_date <= cutoff_date):
                
                if lawyer is None or deadline.responsible_lawyer == lawyer:
                    pending.append(deadline)
        
        # Ordenar por data de vencimento e prioridade
        pending.sort(key=lambda d: (d.due_date, -d.priority))
        return pending
    
    def get_overdue_deadlines(self, lawyer: Optional[str] = None) -> List[LegalDeadline]:
        """Obtém prazos vencidos."""
        today = date.today()
        
        overdue = []
        for deadline in self.deadlines.values():
            if (deadline.status == DeadlineStatus.ATIVO and 
                deadline.due_date < today):
                
                if lawyer is None or deadline.responsible_lawyer == lawyer:
                    overdue.append(deadline)
        
        overdue.sort(key=lambda d: d.due_date)
        return overdue
    
    def complete_deadline(self, deadline_id: str, completion_notes: str = "") -> bool:
        """Marca um prazo como cumprido."""
        deadline = self.deadlines.get(deadline_id)
        if not deadline:
            return False
        
        deadline.status = DeadlineStatus.CUMPRIDO
        deadline.completion_date = date.today()
        deadline.updated_at = datetime.now()
        if completion_notes:
            deadline.notes += f"\nConcluído em {date.today()}: {completion_notes}"
        
        # Cancelar alertas pendentes
        for alert in self.alerts.values():
            if alert.deadline_id == deadline_id and not alert.is_sent:
                alert.is_sent = True  # Marcar como "enviado" para não processar
        
        logger.info(f"Prazo cumprido: {deadline.description}")
        return True
    
    def get_alerts_to_send(self) -> List[DeadlineAlert]:
        """Obtém alertas que devem ser enviados hoje."""
        today = datetime.now().date()
        
        alerts_to_send = []
        for alert in self.alerts.values():
            if (not alert.is_sent and 
                alert.scheduled_date.date() <= today):
                
                # Verificar se o prazo ainda está ativo
                deadline = self.deadlines.get(alert.deadline_id)
                if deadline and deadline.status == DeadlineStatus.ATIVO:
                    alerts_to_send.append(alert)
        
        return alerts_to_send
    
    def send_alert(self, alert_id: str) -> bool:
        """Marca um alerta como enviado."""
        alert = self.alerts.get(alert_id)
        if not alert:
            return False
        
        alert.is_sent = True
        alert.sent_date = datetime.now()
        
        logger.info(f"Alerta enviado: {alert.message}")
        return True
    
    def get_deadline_statistics(self, lawyer: Optional[str] = None, 
                              start_date: Optional[date] = None,
                              end_date: Optional[date] = None) -> Dict[str, Any]:
        """Gera estatísticas de prazos."""
        if not start_date:
            start_date = date.today() - timedelta(days=30)
        if not end_date:
            end_date = date.today()
        
        deadlines = list(self.deadlines.values())
        if lawyer:
            deadlines = [d for d in deadlines if d.responsible_lawyer == lawyer]
        
        # Filtrar por período
        period_deadlines = [
            d for d in deadlines 
            if start_date <= d.due_date <= end_date
        ]
        
        stats = {
            'total_deadlines': len(period_deadlines),
            'completed': len([d for d in period_deadlines if d.status == DeadlineStatus.CUMPRIDO]),
            'overdue': len([d for d in period_deadlines if d.status == DeadlineStatus.ATIVO and d.due_date < date.today()]),
            'pending': len([d for d in period_deadlines if d.status == DeadlineStatus.ATIVO and d.due_date >= date.today()]),
            'by_type': {},
            'by_court': {},
            'average_completion_time': 0.0
        }
        
        # Estatísticas por tipo
        for deadline in period_deadlines:
            deadline_type = deadline.deadline_type.value
            if deadline_type not in stats['by_type']:
                stats['by_type'][deadline_type] = 0
            stats['by_type'][deadline_type] += 1
        
        # Estatísticas por tribunal
        for deadline in period_deadlines:
            court_type = deadline.court_type.value
            if court_type not in stats['by_court']:
                stats['by_court'][court_type] = 0
            stats['by_court'][court_type] += 1
        
        # Tempo médio de conclusão
        completed_deadlines = [d for d in period_deadlines if d.status == DeadlineStatus.CUMPRIDO and d.completion_date]
        if completed_deadlines:
            total_days = sum((d.completion_date - d.created_at.date()).days for d in completed_deadlines)
            stats['average_completion_time'] = total_days / len(completed_deadlines)
        
        return stats
    
    def export_deadlines(self, file_path: str, lawyer: Optional[str] = None):
        """Exporta prazos para arquivo JSON."""
        deadlines_to_export = list(self.deadlines.values())
        if lawyer:
            deadlines_to_export = [d for d in deadlines_to_export if d.responsible_lawyer == lawyer]
        
        # Converter para dicionários
        export_data = []
        for deadline in deadlines_to_export:
            deadline_dict = asdict(deadline)
            
            # Converter enums e datas para strings
            deadline_dict['deadline_type'] = deadline.deadline_type.value
            deadline_dict['status'] = deadline.status.value
            deadline_dict['court_type'] = deadline.court_type.value
            deadline_dict['due_date'] = deadline.due_date.isoformat()
            deadline_dict['created_at'] = deadline.created_at.isoformat()
            deadline_dict['updated_at'] = deadline.updated_at.isoformat()
            
            if deadline.completion_date:
                deadline_dict['completion_date'] = deadline.completion_date.isoformat()
            
            export_data.append(deadline_dict)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Prazos exportados para: {file_path}")

def main():
    """Função principal para demonstração."""
    manager = DeadlineManager()
    
    # Criar alguns prazos de exemplo
    today = date.today()
    
    # Prazo de recurso
    recurso_id = manager.create_deadline(
        process_number="0001234-56.2025.8.26.0100",
        deadline_type=DeadlineType.RECURSO,
        description="Recurso de Apelação - Ação de Cobrança",
        due_date=today + timedelta(days=10),
        court_type=CourtType.ESTADUAL,
        responsible_lawyer="Dr. João Silva",
        client_name="Maria Santos",
        priority=9,
        estimated_hours=8.0,
        notes="Sentença desfavorável - recurso necessário"
    )
    
    # Prazo de contestação
    contestacao_id = manager.create_deadline(
        process_number="0007890-12.2025.5.02.0001",
        deadline_type=DeadlineType.CONTESTACAO,
        description="Contestação - Ação Trabalhista",
        due_date=today + timedelta(days=3),
        court_type=CourtType.TRABALHISTA,
        responsible_lawyer="Dra. Ana Costa",
        client_name="Empresa XYZ Ltda",
        priority=8,
        estimated_hours=6.0
    )
    
    # Calcular prazo a partir de evento
    calculation = manager.calculate_deadline_from_event(
        event_date=today,
        deadline_type=DeadlineType.EMBARGOS,
        court_type=CourtType.FEDERAL,
        custom_days=10
    )
    
    print(f"=== SISTEMA DE GESTÃO DE PRAZOS ===")
    print(f"Prazos criados: {len(manager.deadlines)}")
    
    # Prazos pendentes
    pending = manager.get_pending_deadlines()
    print(f"\nPrazos pendentes ({len(pending)}):")
    for deadline in pending:
        days_left = (deadline.due_date - today).days
        print(f"  - {deadline.description}")
        print(f"    Vencimento: {deadline.due_date.strftime('%d/%m/%Y')} ({days_left} dias)")
        print(f"    Responsável: {deadline.responsible_lawyer}")
        print(f"    Prioridade: {deadline.priority}/10")
    
    # Alertas a enviar
    alerts = manager.get_alerts_to_send()
    print(f"\nAlertas para enviar ({len(alerts)}):")
    for alert in alerts:
        print(f"  - {alert.alert_type.value.upper()}: {alert.message}")
    
    # Cálculo de prazo
    print(f"\nCálculo de prazo:")
    print(f"  Base: {calculation.base_date.strftime('%d/%m/%Y')}")
    print(f"  Tipo: {calculation.deadline_type.value}")
    print(f"  Tribunal: {calculation.court_type.value}")
    print(f"  Resultado: {calculation.calculated_date.strftime('%d/%m/%Y')}")
    print(f"  Dias úteis: {calculation.business_days}")
    print(f"  Detalhes: {calculation.calculation_details}")
    
    # Estatísticas
    stats = manager.get_deadline_statistics()
    print(f"\nEstatísticas:")
    print(f"  Total: {stats['total_deadlines']}")
    print(f"  Cumpridos: {stats['completed']}")
    print(f"  Pendentes: {stats['pending']}")
    print(f"  Vencidos: {stats['overdue']}")
    
    # Exportar prazos
    export_path = "/home/ubuntu/prazos_exemplo.json"
    manager.export_deadlines(export_path)
    print(f"\nPrazos exportados para: {export_path}")

if __name__ == "__main__":
    main()

