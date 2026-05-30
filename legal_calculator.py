#!/usr/bin/env python3
"""
Calculadora Jurídica Avançada com IA
Sistema completo para cálculos jurídicos incluindo trabalhistas, cíveis, atualizações monetárias e juros.
"""

import os
import json
import uuid
import logging
import math
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from decimal import Decimal, ROUND_HALF_UP

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CalculationType(Enum):
    TRABALHISTA = "trabalhista"
    ATUALIZACAO_MONETARIA = "atualizacao_monetaria"
    JUROS_SIMPLES = "juros_simples"
    JUROS_COMPOSTOS = "juros_compostos"
    HONORARIOS_ADVOCATICIOS = "honorarios_advocaticios"
    MULTA_CONTRATUAL = "multa_contratual"
    DANOS_MORAIS = "danos_morais"
    EXECUCAO_TITULO = "execucao_titulo"
    REVISAO_CONTRATUAL = "revisao_contratual"

class IndexType(Enum):
    IPCA = "ipca"
    IGP_M = "igp_m"
    INPC = "inpc"
    SELIC = "selic"
    TR = "tr"
    INCC = "incc"

@dataclass
class EconomicIndex:
    index_type: IndexType
    reference_date: date
    value: float
    accumulated_12m: float
    source: str

@dataclass
class CalculationInput:
    calculation_id: str
    calculation_type: CalculationType
    principal_value: Decimal
    start_date: date
    end_date: date
    interest_rate: Optional[Decimal] = None
    index_type: Optional[IndexType] = None
    additional_parameters: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.additional_parameters is None:
            self.additional_parameters = {}

@dataclass
class CalculationResult:
    calculation_id: str
    calculation_type: CalculationType
    principal_value: Decimal
    updated_value: Decimal
    interest_value: Decimal
    total_value: Decimal
    calculation_details: List[Dict[str, Any]]
    methodology: str
    legal_basis: List[str]
    calculated_at: datetime
    period_days: int
    effective_rate: Decimal

@dataclass
class LaborCalculation:
    """Cálculo trabalhista específico."""
    employee_name: str
    admission_date: date
    termination_date: date
    salary: Decimal
    worked_hours: int
    overtime_hours: int
    night_hours: int
    vacation_days: int
    thirteenth_salary: bool
    fgts_deposit: bool
    notice_period: int
    severance_components: Dict[str, Decimal]

class EconomicIndexManager:
    """Gerenciador de índices econômicos."""
    
    def __init__(self):
        # Dados simulados de índices (em produção, seria integrado com APIs do BACEN)
        self._initialize_sample_indices()
    
    def _initialize_sample_indices(self):
        """Inicializa índices econômicos simulados."""
        self.indices = {
            IndexType.IPCA: [
                EconomicIndex(IndexType.IPCA, date(2024, 1, 1), 0.42, 4.62, "IBGE"),
                EconomicIndex(IndexType.IPCA, date(2024, 2, 1), 0.83, 4.50, "IBGE"),
                EconomicIndex(IndexType.IPCA, date(2024, 3, 1), 0.16, 3.93, "IBGE"),
                EconomicIndex(IndexType.IPCA, date(2024, 4, 1), 0.38, 3.69, "IBGE"),
                EconomicIndex(IndexType.IPCA, date(2024, 5, 1), 0.46, 3.93, "IBGE"),
                EconomicIndex(IndexType.IPCA, date(2024, 6, 1), 0.21, 4.23, "IBGE"),
                EconomicIndex(IndexType.IPCA, date(2024, 7, 1), 0.38, 4.50, "IBGE"),
                EconomicIndex(IndexType.IPCA, date(2024, 8, 1), 0.02, 4.24, "IBGE"),
            ],
            IndexType.SELIC: [
                EconomicIndex(IndexType.SELIC, date(2024, 1, 1), 11.75, 11.75, "BACEN"),
                EconomicIndex(IndexType.SELIC, date(2024, 2, 1), 11.25, 11.25, "BACEN"),
                EconomicIndex(IndexType.SELIC, date(2024, 3, 1), 10.75, 10.75, "BACEN"),
                EconomicIndex(IndexType.SELIC, date(2024, 4, 1), 10.50, 10.50, "BACEN"),
                EconomicIndex(IndexType.SELIC, date(2024, 5, 1), 10.50, 10.50, "BACEN"),
                EconomicIndex(IndexType.SELIC, date(2024, 6, 1), 10.50, 10.50, "BACEN"),
                EconomicIndex(IndexType.SELIC, date(2024, 7, 1), 10.50, 10.50, "BACEN"),
                EconomicIndex(IndexType.SELIC, date(2024, 8, 1), 10.50, 10.50, "BACEN"),
            ]
        }
    
    def get_index_value(self, index_type: IndexType, reference_date: date) -> Optional[EconomicIndex]:
        """Obtém valor de índice para uma data específica."""
        if index_type not in self.indices:
            return None
        
        # Encontrar o índice mais próximo da data
        indices = self.indices[index_type]
        closest_index = None
        min_diff = float('inf')
        
        for index in indices:
            diff = abs((reference_date - index.reference_date).days)
            if diff < min_diff:
                min_diff = diff
                closest_index = index
        
        return closest_index
    
    def calculate_accumulated_index(self, index_type: IndexType, start_date: date, end_date: date) -> Decimal:
        """Calcula índice acumulado entre duas datas."""
        if index_type not in self.indices:
            return Decimal('0')
        
        indices = self.indices[index_type]
        accumulated = Decimal('1')
        
        current_date = start_date
        while current_date <= end_date:
            # Encontrar índice do mês
            month_start = current_date.replace(day=1)
            index = self.get_index_value(index_type, month_start)
            
            if index:
                monthly_rate = Decimal(str(index.value)) / Decimal('100')
                accumulated *= (Decimal('1') + monthly_rate)
            
            # Próximo mês
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
        
        return accumulated - Decimal('1')  # Retorna apenas o percentual de correção

class LegalCalculator:
    """Calculadora jurídica principal."""
    
    def __init__(self):
        self.index_manager = EconomicIndexManager()
        self.calculations: Dict[str, CalculationResult] = {}
        
        # Taxas e parâmetros legais
        self.legal_rates = {
            'juros_mora_civil': Decimal('0.01'),  # 1% ao mês (art. 406 CC)
            'juros_mora_trabalhista': Decimal('0.01'),  # 1% ao mês
            'honorarios_minimo': Decimal('0.10'),  # 10% mínimo
            'honorarios_maximo': Decimal('0.20'),  # 20% máximo
            'multa_clt': Decimal('0.40'),  # 40% FGTS (art. 18 Lei 8036/90)
        }
    
    def calculate_monetary_update(self, principal: Decimal, start_date: date, 
                                end_date: date, index_type: IndexType) -> CalculationResult:
        """Calcula atualização monetária."""
        calculation_id = str(uuid.uuid4())
        
        # Calcular correção pelo índice
        correction_rate = self.index_manager.calculate_accumulated_index(index_type, start_date, end_date)
        updated_value = principal * (Decimal('1') + correction_rate)
        correction_value = updated_value - principal
        
        # Detalhes do cálculo
        period_days = (end_date - start_date).days
        
        calculation_details = [
            {
                'description': 'Valor Principal',
                'value': float(principal),
                'date': start_date.isoformat()
            },
            {
                'description': f'Correção {index_type.value.upper()}',
                'rate': float(correction_rate * 100),
                'value': float(correction_value),
                'period': f'{period_days} dias'
            },
            {
                'description': 'Valor Atualizado',
                'value': float(updated_value),
                'date': end_date.isoformat()
            }
        ]
        
        legal_basis = [
            f"Correção monetária pelo {index_type.value.upper()}",
            "Lei 6.899/81 - Correção monetária",
            "Súmula 43 do STJ - Juros moratórios"
        ]
        
        methodology = f"""
        Cálculo de atualização monetária utilizando o índice {index_type.value.upper()}.
        
        Fórmula aplicada:
        Valor Atualizado = Valor Principal × (1 + Taxa de Correção)
        
        Onde:
        - Valor Principal: R$ {principal:,.2f}
        - Taxa de Correção: {correction_rate * 100:.4f}%
        - Período: {period_days} dias ({start_date.strftime('%d/%m/%Y')} a {end_date.strftime('%d/%m/%Y')})
        """
        
        result = CalculationResult(
            calculation_id=calculation_id,
            calculation_type=CalculationType.ATUALIZACAO_MONETARIA,
            principal_value=principal,
            updated_value=updated_value,
            interest_value=Decimal('0'),
            total_value=updated_value,
            calculation_details=calculation_details,
            methodology=methodology,
            legal_basis=legal_basis,
            calculated_at=datetime.now(),
            period_days=period_days,
            effective_rate=correction_rate
        )
        
        self.calculations[calculation_id] = result
        logger.info(f"Atualização monetária calculada: {calculation_id}")
        return result
    
    def calculate_simple_interest(self, principal: Decimal, start_date: date, 
                                end_date: date, monthly_rate: Decimal) -> CalculationResult:
        """Calcula juros simples."""
        calculation_id = str(uuid.uuid4())
        
        period_days = (end_date - start_date).days
        period_months = Decimal(str(period_days)) / Decimal('30')  # Aproximação
        
        # Juros simples: J = C × i × t
        interest_value = principal * monthly_rate * period_months
        total_value = principal + interest_value
        
        calculation_details = [
            {
                'description': 'Valor Principal',
                'value': float(principal),
                'date': start_date.isoformat()
            },
            {
                'description': 'Juros Simples',
                'rate': float(monthly_rate * 100),
                'period_months': float(period_months),
                'value': float(interest_value),
                'formula': 'J = C × i × t'
            },
            {
                'description': 'Valor Total',
                'value': float(total_value),
                'date': end_date.isoformat()
            }
        ]
        
        legal_basis = [
            "Art. 406 do Código Civil - Juros moratórios",
            "Art. 161, §1º do CTN - Juros de mora",
            "Súmula 54 do STJ - Juros moratórios"
        ]
        
        methodology = f"""
        Cálculo de juros simples conforme legislação civil.
        
        Fórmula aplicada:
        J = C × i × t
        
        Onde:
        - C (Capital): R$ {principal:,.2f}
        - i (Taxa mensal): {monthly_rate * 100:.2f}%
        - t (Tempo): {period_months:.2f} meses ({period_days} dias)
        - J (Juros): R$ {interest_value:,.2f}
        """
        
        result = CalculationResult(
            calculation_id=calculation_id,
            calculation_type=CalculationType.JUROS_SIMPLES,
            principal_value=principal,
            updated_value=principal,
            interest_value=interest_value,
            total_value=total_value,
            calculation_details=calculation_details,
            methodology=methodology,
            legal_basis=legal_basis,
            calculated_at=datetime.now(),
            period_days=period_days,
            effective_rate=monthly_rate
        )
        
        self.calculations[calculation_id] = result
        logger.info(f"Juros simples calculados: {calculation_id}")
        return result
    
    def calculate_legal_fees(self, case_value: Decimal, complexity: str = "normal", 
                           success_rate: float = 1.0) -> CalculationResult:
        """Calcula honorários advocatícios."""
        calculation_id = str(uuid.uuid4())
        
        # Determinar percentual baseado na complexidade
        complexity_rates = {
            "simples": Decimal('0.10'),    # 10%
            "normal": Decimal('0.15'),     # 15%
            "complexo": Decimal('0.20')    # 20%
        }
        
        base_rate = complexity_rates.get(complexity, Decimal('0.15'))
        
        # Ajustar pela taxa de sucesso
        adjusted_rate = base_rate * Decimal(str(success_rate))
        
        # Calcular honorários
        fees_value = case_value * adjusted_rate
        
        calculation_details = [
            {
                'description': 'Valor da Causa',
                'value': float(case_value)
            },
            {
                'description': f'Taxa Base ({complexity})',
                'rate': float(base_rate * 100),
                'value': float(case_value * base_rate)
            },
            {
                'description': 'Ajuste por Sucesso',
                'success_rate': success_rate,
                'adjusted_rate': float(adjusted_rate * 100),
                'value': float(fees_value)
            }
        ]
        
        legal_basis = [
            "Art. 85 do CPC - Honorários advocatícios",
            "Art. 22 da Lei 8.906/94 - Estatuto da OAB",
            "Tabela de honorários da OAB"
        ]
        
        methodology = f"""
        Cálculo de honorários advocatícios conforme CPC e Estatuto da OAB.
        
        Critérios considerados:
        - Valor da causa: R$ {case_value:,.2f}
        - Complexidade: {complexity}
        - Taxa base: {base_rate * 100:.1f}%
        - Taxa de sucesso: {success_rate * 100:.0f}%
        - Taxa final: {adjusted_rate * 100:.2f}%
        """
        
        result = CalculationResult(
            calculation_id=calculation_id,
            calculation_type=CalculationType.HONORARIOS_ADVOCATICIOS,
            principal_value=case_value,
            updated_value=case_value,
            interest_value=Decimal('0'),
            total_value=fees_value,
            calculation_details=calculation_details,
            methodology=methodology,
            legal_basis=legal_basis,
            calculated_at=datetime.now(),
            period_days=0,
            effective_rate=adjusted_rate
        )
        
        self.calculations[calculation_id] = result
        logger.info(f"Honorários advocatícios calculados: {calculation_id}")
        return result
    
    def calculate_labor_termination(self, labor_calc: LaborCalculation) -> CalculationResult:
        """Calcula verbas rescisórias trabalhistas."""
        calculation_id = str(uuid.uuid4())
        
        # Calcular componentes
        components = {}
        
        # Saldo de salário
        worked_days = (labor_calc.termination_date - labor_calc.admission_date).days
        if worked_days > 0:
            daily_salary = labor_calc.salary / Decimal('30')
            # Calcular dias do mês de rescisão
            month_days = labor_calc.termination_date.day
            components['saldo_salario'] = daily_salary * Decimal(str(month_days))
        
        # Aviso prévio
        if labor_calc.notice_period > 0:
            components['aviso_previo'] = labor_calc.salary * Decimal(str(labor_calc.notice_period)) / Decimal('30')
        
        # 13º salário proporcional
        if labor_calc.thirteenth_salary:
            months_worked = (labor_calc.termination_date.month - labor_calc.admission_date.month) + 1
            components['decimo_terceiro'] = (labor_calc.salary / Decimal('12')) * Decimal(str(months_worked))
        
        # Férias proporcionais
        if labor_calc.vacation_days > 0:
            components['ferias_proporcionais'] = (labor_calc.salary / Decimal('30')) * Decimal(str(labor_calc.vacation_days))
            components['um_terco_ferias'] = components['ferias_proporcionais'] / Decimal('3')
        
        # FGTS + 40%
        if labor_calc.fgts_deposit:
            fgts_base = sum(components.values())
            components['fgts'] = fgts_base * Decimal('0.08')  # 8% FGTS
            components['multa_fgts'] = components['fgts'] * Decimal('0.40')  # 40% multa
        
        # Horas extras
        if labor_calc.overtime_hours > 0:
            hour_value = labor_calc.salary / Decimal('220')  # 220h mensais
            overtime_value = hour_value * Decimal('1.5') * Decimal(str(labor_calc.overtime_hours))
            components['horas_extras'] = overtime_value
        
        total_value = sum(components.values())
        
        calculation_details = []
        for component, value in components.items():
            calculation_details.append({
                'description': component.replace('_', ' ').title(),
                'value': float(value),
                'calculation': f"Conforme CLT"
            })
        
        calculation_details.append({
            'description': 'Total das Verbas Rescisórias',
            'value': float(total_value)
        })
        
        legal_basis = [
            "Art. 477 da CLT - Rescisão do contrato",
            "Art. 18 da Lei 8.036/90 - Multa FGTS",
            "Súmula 261 do TST - Férias proporcionais",
            "Art. 7º, XVI da CF - 13º salário"
        ]
        
        methodology = f"""
        Cálculo de verbas rescisórias trabalhistas conforme CLT.
        
        Dados do empregado:
        - Nome: {labor_calc.employee_name}
        - Admissão: {labor_calc.admission_date.strftime('%d/%m/%Y')}
        - Demissão: {labor_calc.termination_date.strftime('%d/%m/%Y')}
        - Salário: R$ {labor_calc.salary:,.2f}
        
        Componentes calculados:
        {chr(10).join([f"- {k.replace('_', ' ').title()}: R$ {v:,.2f}" for k, v in components.items()])}
        """
        
        result = CalculationResult(
            calculation_id=calculation_id,
            calculation_type=CalculationType.TRABALHISTA,
            principal_value=labor_calc.salary,
            updated_value=labor_calc.salary,
            interest_value=Decimal('0'),
            total_value=total_value,
            calculation_details=calculation_details,
            methodology=methodology,
            legal_basis=legal_basis,
            calculated_at=datetime.now(),
            period_days=(labor_calc.termination_date - labor_calc.admission_date).days,
            effective_rate=Decimal('0')
        )
        
        self.calculations[calculation_id] = result
        logger.info(f"Cálculo trabalhista realizado: {calculation_id}")
        return result
    
    def calculate_compound_interest_with_correction(self, principal: Decimal, start_date: date,
                                                  end_date: date, index_type: IndexType,
                                                  interest_rate: Decimal) -> CalculationResult:
        """Calcula correção monetária + juros compostos."""
        calculation_id = str(uuid.uuid4())
        
        # Primeiro aplicar correção monetária
        correction_rate = self.index_manager.calculate_accumulated_index(index_type, start_date, end_date)
        corrected_value = principal * (Decimal('1') + correction_rate)
        
        # Depois aplicar juros sobre o valor corrigido
        period_days = (end_date - start_date).days
        period_months = Decimal(str(period_days)) / Decimal('30')
        
        # Juros compostos: M = C × (1 + i)^t
        compound_factor = (Decimal('1') + interest_rate) ** period_months
        final_value = corrected_value * compound_factor
        
        interest_value = final_value - corrected_value
        correction_value = corrected_value - principal
        
        calculation_details = [
            {
                'description': 'Valor Principal',
                'value': float(principal),
                'date': start_date.isoformat()
            },
            {
                'description': f'Correção {index_type.value.upper()}',
                'rate': float(correction_rate * 100),
                'value': float(correction_value)
            },
            {
                'description': 'Valor Corrigido',
                'value': float(corrected_value)
            },
            {
                'description': 'Juros Compostos',
                'rate': float(interest_rate * 100),
                'period_months': float(period_months),
                'value': float(interest_value),
                'formula': 'M = C × (1 + i)^t'
            },
            {
                'description': 'Valor Final',
                'value': float(final_value),
                'date': end_date.isoformat()
            }
        ]
        
        legal_basis = [
            f"Correção monetária pelo {index_type.value.upper()}",
            "Art. 406 do Código Civil - Juros moratórios",
            "Súmula 562 do STF - Juros compostos"
        ]
        
        methodology = f"""
        Cálculo de correção monetária + juros compostos.
        
        Etapas do cálculo:
        1. Correção monetária: {correction_rate * 100:.4f}%
        2. Juros compostos: {interest_rate * 100:.2f}% a.m.
        
        Fórmulas aplicadas:
        - Correção: Valor × (1 + Taxa de Correção)
        - Juros: Valor Corrigido × (1 + Taxa de Juros)^Período
        """
        
        result = CalculationResult(
            calculation_id=calculation_id,
            calculation_type=CalculationType.JUROS_COMPOSTOS,
            principal_value=principal,
            updated_value=corrected_value,
            interest_value=interest_value,
            total_value=final_value,
            calculation_details=calculation_details,
            methodology=methodology,
            legal_basis=legal_basis,
            calculated_at=datetime.now(),
            period_days=period_days,
            effective_rate=interest_rate
        )
        
        self.calculations[calculation_id] = result
        logger.info(f"Correção + juros compostos calculados: {calculation_id}")
        return result
    
    def export_calculation(self, calculation_id: str, output_path: str):
        """Exporta cálculo para arquivo."""
        calculation = self.calculations.get(calculation_id)
        if not calculation:
            raise ValueError(f"Cálculo {calculation_id} não encontrado")
        
        # Converter para dicionário
        calc_dict = asdict(calculation)
        
        # Converter enums e decimais
        calc_dict['calculation_type'] = calculation.calculation_type.value
        calc_dict['calculated_at'] = calculation.calculated_at.isoformat()
        calc_dict['principal_value'] = float(calculation.principal_value)
        calc_dict['updated_value'] = float(calculation.updated_value)
        calc_dict['interest_value'] = float(calculation.interest_value)
        calc_dict['total_value'] = float(calculation.total_value)
        calc_dict['effective_rate'] = float(calculation.effective_rate)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(calc_dict, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Cálculo exportado para: {output_path}")

def main():
    """Função principal para demonstração."""
    calculator = LegalCalculator()
    
    print("=== CALCULADORA JURÍDICA AVANÇADA ===")
    
    # 1. Atualização monetária
    print("\n1. ATUALIZAÇÃO MONETÁRIA (IPCA)")
    result1 = calculator.calculate_monetary_update(
        principal=Decimal('10000.00'),
        start_date=date(2024, 1, 1),
        end_date=date(2024, 8, 31),
        index_type=IndexType.IPCA
    )
    
    print(f"Valor principal: R$ {result1.principal_value:,.2f}")
    print(f"Valor atualizado: R$ {result1.total_value:,.2f}")
    print(f"Correção: R$ {result1.total_value - result1.principal_value:,.2f}")
    print(f"Taxa efetiva: {result1.effective_rate * 100:.4f}%")
    
    # 2. Juros simples
    print("\n2. JUROS SIMPLES (1% a.m.)")
    result2 = calculator.calculate_simple_interest(
        principal=Decimal('5000.00'),
        start_date=date(2024, 1, 1),
        end_date=date(2024, 6, 30),
        monthly_rate=Decimal('0.01')
    )
    
    print(f"Valor principal: R$ {result2.principal_value:,.2f}")
    print(f"Juros: R$ {result2.interest_value:,.2f}")
    print(f"Total: R$ {result2.total_value:,.2f}")
    
    # 3. Honorários advocatícios
    print("\n3. HONORÁRIOS ADVOCATÍCIOS")
    result3 = calculator.calculate_legal_fees(
        case_value=Decimal('50000.00'),
        complexity="complexo",
        success_rate=0.8
    )
    
    print(f"Valor da causa: R$ {result3.principal_value:,.2f}")
    print(f"Honorários: R$ {result3.total_value:,.2f}")
    print(f"Percentual: {result3.effective_rate * 100:.2f}%")
    
    # 4. Cálculo trabalhista
    print("\n4. CÁLCULO TRABALHISTA")
    labor_calc = LaborCalculation(
        employee_name="João Silva",
        admission_date=date(2023, 1, 15),
        termination_date=date(2024, 8, 30),
        salary=Decimal('3000.00'),
        worked_hours=1760,
        overtime_hours=50,
        night_hours=0,
        vacation_days=20,
        thirteenth_salary=True,
        fgts_deposit=True,
        notice_period=30,
        severance_components={}
    )
    
    result4 = calculator.calculate_labor_termination(labor_calc)
    
    print(f"Empregado: {labor_calc.employee_name}")
    print(f"Período: {labor_calc.admission_date.strftime('%d/%m/%Y')} a {labor_calc.termination_date.strftime('%d/%m/%Y')}")
    print(f"Salário: R$ {labor_calc.salary:,.2f}")
    print(f"Total rescisório: R$ {result4.total_value:,.2f}")
    
    # 5. Correção + Juros compostos
    print("\n5. CORREÇÃO MONETÁRIA + JUROS COMPOSTOS")
    result5 = calculator.calculate_compound_interest_with_correction(
        principal=Decimal('20000.00'),
        start_date=date(2024, 1, 1),
        end_date=date(2024, 8, 31),
        index_type=IndexType.IPCA,
        interest_rate=Decimal('0.01')
    )
    
    print(f"Valor principal: R$ {result5.principal_value:,.2f}")
    print(f"Valor corrigido: R$ {result5.updated_value:,.2f}")
    print(f"Juros: R$ {result5.interest_value:,.2f}")
    print(f"Total final: R$ {result5.total_value:,.2f}")
    
    # Exportar cálculos
    print(f"\n=== EXPORTAÇÃO ===")
    for i, (calc_id, result) in enumerate(calculator.calculations.items(), 1):
        export_path = f"/home/ubuntu/calculo_{i}_{result.calculation_type.value}.json"
        calculator.export_calculation(calc_id, export_path)
        print(f"Cálculo {i} exportado: {export_path}")
    
    print(f"\nTotal de cálculos realizados: {len(calculator.calculations)}")

if __name__ == "__main__":
    main()

