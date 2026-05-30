#!/usr/bin/env python3
"""
Calculadora Jurídica Avançada - Versão Melhorada
Implementa melhorias: mais tipos de cálculo, maior precisão
e validações aprimoradas
"""

import json
import math
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from decimal import Decimal, ROUND_HALF_UP
import calendar

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CalculationType(Enum):
    """Tipos de cálculo"""
    TRABALHISTA = "Trabalhista"
    CIVIL = "Civil"
    PREVIDENCIARIO = "Previdenciário"
    TRIBUTARIO = "Tributário"
    CONSUMIDOR = "Consumidor"
    FAMILIA = "Família"

class WorkerCalculationType(Enum):
    """Tipos de cálculo trabalhista"""
    RESCISAO = "Rescisão"
    HORAS_EXTRAS = "Horas Extras"
    ADICIONAL_NOTURNO = "Adicional Noturno"
    FERIAS = "Férias"
    DECIMO_TERCEIRO = "13º Salário"
    FGTS = "FGTS"
    INSS = "INSS"
    IRRF = "IRRF"
    MULTA_FGTS = "Multa FGTS"

class CivilCalculationType(Enum):
    """Tipos de cálculo civil"""
    DANOS_MORAIS = "Danos Morais"
    JUROS_MORA = "Juros de Mora"
    CORRECAO_MONETARIA = "Correção Monetária"
    HONORARIOS = "Honorários Advocatícios"
    CUSTAS = "Custas Processuais"

@dataclass
class CalculationInput:
    """Entrada para cálculo"""
    id: str
    calculation_type: CalculationType
    subtype: str
    parameters: Dict[str, Any]
    user_id: str
    timestamp: datetime

@dataclass
class CalculationResult:
    """Resultado de cálculo"""
    id: str
    input_id: str
    result_value: Decimal
    breakdown: Dict[str, Any]
    formulas_used: List[str]
    legal_basis: List[str]
    calculation_date: datetime
    metadata: Dict[str, Any]

class TaxTables:
    """Tabelas de impostos e contribuições"""
    
    @staticmethod
    def get_inss_table(year: int = 2024) -> List[Tuple[Decimal, Decimal, Decimal]]:
        """Retorna tabela INSS (faixa_min, faixa_max, aliquota)"""
        if year >= 2024:
            return [
                (Decimal('0.00'), Decimal('1412.00'), Decimal('0.075')),
                (Decimal('1412.01'), Decimal('2666.68'), Decimal('0.09')),
                (Decimal('2666.69'), Decimal('4000.03'), Decimal('0.12')),
                (Decimal('4000.04'), Decimal('7786.02'), Decimal('0.14'))
            ]
        else:
            # Tabela anterior (simplificada)
            return [
                (Decimal('0.00'), Decimal('1320.00'), Decimal('0.075')),
                (Decimal('1320.01'), Decimal('2571.29'), Decimal('0.09')),
                (Decimal('2571.30'), Decimal('3856.94'), Decimal('0.12')),
                (Decimal('3856.95'), Decimal('7507.49'), Decimal('0.14'))
            ]
    
    @staticmethod
    def get_irrf_table(year: int = 2024) -> List[Tuple[Decimal, Decimal, Decimal, Decimal]]:
        """Retorna tabela IRRF (faixa_min, faixa_max, aliquota, deducao)"""
        if year >= 2024:
            return [
                (Decimal('0.00'), Decimal('2259.20'), Decimal('0.00'), Decimal('0.00')),
                (Decimal('2259.21'), Decimal('2826.65'), Decimal('0.075'), Decimal('169.44')),
                (Decimal('2826.66'), Decimal('3751.05'), Decimal('0.15'), Decimal('381.44')),
                (Decimal('3751.06'), Decimal('4664.68'), Decimal('0.225'), Decimal('662.77')),
                (Decimal('4664.69'), Decimal('999999.99'), Decimal('0.275'), Decimal('896.00'))
            ]
        else:
            return [
                (Decimal('0.00'), Decimal('2112.00'), Decimal('0.00'), Decimal('0.00')),
                (Decimal('2112.01'), Decimal('2826.65'), Decimal('0.075'), Decimal('158.40')),
                (Decimal('2826.66'), Decimal('3751.05'), Decimal('0.15'), Decimal('370.40')),
                (Decimal('3751.06'), Decimal('4664.68'), Decimal('0.225'), Decimal('651.73')),
                (Decimal('4664.69'), Decimal('999999.99'), Decimal('0.275'), Decimal('884.96'))
            ]

class LegalIndices:
    """Índices legais para correção monetária"""
    
    @staticmethod
    def get_selic_rate(year: int, month: int) -> Decimal:
        """Taxa SELIC mensal (simulada)"""
        # Valores aproximados para demonstração
        rates = {
            (2024, 1): Decimal('0.0095'),
            (2024, 2): Decimal('0.0098'),
            (2024, 3): Decimal('0.0102'),
            (2024, 4): Decimal('0.0105'),
            (2024, 5): Decimal('0.0108'),
            (2024, 6): Decimal('0.0110'),
            (2024, 7): Decimal('0.0112'),
            (2024, 8): Decimal('0.0115'),
            (2024, 9): Decimal('0.0118'),
            (2024, 10): Decimal('0.0120'),
            (2024, 11): Decimal('0.0122'),
            (2024, 12): Decimal('0.0125')
        }
        return rates.get((year, month), Decimal('0.01'))
    
    @staticmethod
    def get_ipca_rate(year: int, month: int) -> Decimal:
        """Taxa IPCA mensal (simulada)"""
        # Valores aproximados para demonstração
        rates = {
            (2024, 1): Decimal('0.0042'),
            (2024, 2): Decimal('0.0038'),
            (2024, 3): Decimal('0.0045'),
            (2024, 4): Decimal('0.0041'),
            (2024, 5): Decimal('0.0039'),
            (2024, 6): Decimal('0.0043'),
            (2024, 7): Decimal('0.0047'),
            (2024, 8): Decimal('0.0044'),
            (2024, 9): Decimal('0.0046'),
            (2024, 10): Decimal('0.0048'),
            (2024, 11): Decimal('0.0050'),
            (2024, 12): Decimal('0.0052')
        }
        return rates.get((year, month), Decimal('0.004'))

class EnhancedLegalCalculator:
    """Calculadora jurídica aprimorada"""
    
    def __init__(self):
        self.calculations_history = {}
        self.tax_tables = TaxTables()
        self.legal_indices = LegalIndices()
    
    def calculate(self, calc_input: CalculationInput) -> CalculationResult:
        """Executa cálculo baseado no tipo"""
        logger.info(f"Executando cálculo: {calc_input.calculation_type.value} - {calc_input.subtype}")
        
        if calc_input.calculation_type == CalculationType.TRABALHISTA:
            return self._calculate_trabalhista(calc_input)
        elif calc_input.calculation_type == CalculationType.CIVIL:
            return self._calculate_civil(calc_input)
        elif calc_input.calculation_type == CalculationType.PREVIDENCIARIO:
            return self._calculate_previdenciario(calc_input)
        elif calc_input.calculation_type == CalculationType.TRIBUTARIO:
            return self._calculate_tributario(calc_input)
        else:
            raise ValueError(f"Tipo de cálculo não suportado: {calc_input.calculation_type}")
    
    def _calculate_trabalhista(self, calc_input: CalculationInput) -> CalculationResult:
        """Cálculos trabalhistas"""
        subtype = calc_input.subtype
        params = calc_input.parameters
        
        if subtype == WorkerCalculationType.RESCISAO.value:
            return self._calculate_rescisao(calc_input)
        elif subtype == WorkerCalculationType.HORAS_EXTRAS.value:
            return self._calculate_horas_extras(calc_input)
        elif subtype == WorkerCalculationType.FERIAS.value:
            return self._calculate_ferias(calc_input)
        elif subtype == WorkerCalculationType.DECIMO_TERCEIRO.value:
            return self._calculate_decimo_terceiro(calc_input)
        elif subtype == WorkerCalculationType.FGTS.value:
            return self._calculate_fgts(calc_input)
        else:
            raise ValueError(f"Subtipo trabalhista não suportado: {subtype}")
    
    def _calculate_rescisao(self, calc_input: CalculationInput) -> CalculationResult:
        """Cálculo de rescisão trabalhista"""
        params = calc_input.parameters
        
        salario = Decimal(str(params['salario']))
        data_admissao = datetime.strptime(params['data_admissao'], '%Y-%m-%d')
        data_demissao = datetime.strptime(params['data_demissao'], '%Y-%m-%d')
        tipo_rescisao = params['tipo_rescisao']  # 'sem_justa_causa', 'com_justa_causa', 'pedido_demissao'
        aviso_previo_trabalhado = params.get('aviso_previo_trabalhado', False)
        
        # Calcula tempo de serviço
        tempo_servico = data_demissao - data_admissao
        anos_servico = tempo_servico.days / 365.25
        
        breakdown = {}
        formulas = []
        legal_basis = []
        
        # Saldo de salário (proporcional)
        dias_trabalhados = (data_demissao.day)
        saldo_salario = (salario / 30) * Decimal(str(dias_trabalhados))
        breakdown['saldo_salario'] = saldo_salario
        formulas.append(f"Saldo salário = (R$ {salario} / 30) × {dias_trabalhados} dias")
        
        # 13º salário proporcional
        meses_trabalhados = data_demissao.month
        decimo_terceiro = (salario / 12) * Decimal(str(meses_trabalhados))
        breakdown['decimo_terceiro'] = decimo_terceiro
        formulas.append(f"13º proporcional = (R$ {salario} / 12) × {meses_trabalhados} meses")
        
        # Férias proporcionais + 1/3
        ferias_proporcionais = (salario / 12) * Decimal(str(meses_trabalhados))
        um_terco_ferias = ferias_proporcionais / 3
        breakdown['ferias_proporcionais'] = ferias_proporcionais
        breakdown['um_terco_ferias'] = um_terco_ferias
        formulas.append(f"Férias proporcionais = (R$ {salario} / 12) × {meses_trabalhados} meses")
        formulas.append(f"1/3 férias = R$ {ferias_proporcionais} / 3")
        
        total = saldo_salario + decimo_terceiro + ferias_proporcionais + um_terco_ferias
        
        # Verbas específicas por tipo de rescisão
        if tipo_rescisao == 'sem_justa_causa':
            # Aviso prévio
            if not aviso_previo_trabalhado:
                aviso_previo = salario
                breakdown['aviso_previo'] = aviso_previo
                total += aviso_previo
                formulas.append(f"Aviso prévio indenizado = R$ {salario}")
            
            # Multa FGTS 40%
            fgts_depositado = salario * Decimal('0.08') * Decimal(str(int(anos_servico * 12)))
            multa_fgts = fgts_depositado * Decimal('0.40')
            breakdown['multa_fgts'] = multa_fgts
            total += multa_fgts
            formulas.append(f"Multa FGTS 40% = R$ {fgts_depositado} × 0,40")
            
            # Seguro desemprego (informativo)
            breakdown['seguro_desemprego'] = "Direito adquirido (consultar CAIXA)"
            
            legal_basis.extend([
                "Art. 477 da CLT - Rescisão do contrato",
                "Art. 18, §1º da Lei 8.036/90 - Multa FGTS",
                "Lei 7.998/90 - Seguro desemprego"
            ])
        
        elif tipo_rescisao == 'pedido_demissao':
            # Sem aviso prévio, sem multa FGTS, sem seguro desemprego
            legal_basis.append("Art. 487, §4º da CLT - Pedido de demissão")
        
        # Descontos
        desconto_inss = self._calculate_inss(salario)
        desconto_irrf = self._calculate_irrf(salario - desconto_inss)
        
        breakdown['desconto_inss'] = desconto_inss
        breakdown['desconto_irrf'] = desconto_irrf
        
        total_liquido = total - desconto_inss - desconto_irrf
        
        result = CalculationResult(
            id=f"calc_{int(datetime.now().timestamp())}",
            input_id=calc_input.id,
            result_value=total_liquido.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
            breakdown=self._decimal_to_float_dict(breakdown),
            formulas_used=formulas,
            legal_basis=legal_basis,
            calculation_date=datetime.now(),
            metadata={
                "tipo_rescisao": tipo_rescisao,
                "tempo_servico_anos": round(anos_servico, 2),
                "total_bruto": float(total),
                "total_descontos": float(desconto_inss + desconto_irrf)
            }
        )
        
        self.calculations_history[result.id] = result
        return result
    
    def _calculate_horas_extras(self, calc_input: CalculationInput) -> CalculationResult:
        """Cálculo de horas extras"""
        params = calc_input.parameters
        
        salario_base = Decimal(str(params['salario_base']))
        horas_extras_50 = Decimal(str(params.get('horas_extras_50', 0)))  # 50%
        horas_extras_100 = Decimal(str(params.get('horas_extras_100', 0)))  # 100%
        meses = Decimal(str(params.get('meses', 1)))
        
        # Valor da hora normal
        valor_hora = salario_base / 220  # 220 horas mensais
        
        # Horas extras 50%
        valor_he_50 = valor_hora * Decimal('1.5')
        total_he_50 = valor_he_50 * horas_extras_50 * meses
        
        # Horas extras 100%
        valor_he_100 = valor_hora * Decimal('2.0')
        total_he_100 = valor_he_100 * horas_extras_100 * meses
        
        total_horas_extras = total_he_50 + total_he_100
        
        # Reflexos
        reflexo_13 = total_horas_extras / 12
        reflexo_ferias = total_horas_extras / 12
        reflexo_ferias_terco = reflexo_ferias / 3
        reflexo_fgts = total_horas_extras * Decimal('0.08')
        
        total_reflexos = reflexo_13 + reflexo_ferias + reflexo_ferias_terco + reflexo_fgts
        total_geral = total_horas_extras + total_reflexos
        
        breakdown = {
            "valor_hora_normal": valor_hora,
            "valor_he_50": valor_he_50,
            "valor_he_100": valor_he_100,
            "total_he_50": total_he_50,
            "total_he_100": total_he_100,
            "total_horas_extras": total_horas_extras,
            "reflexo_13_salario": reflexo_13,
            "reflexo_ferias": reflexo_ferias,
            "reflexo_ferias_terco": reflexo_ferias_terco,
            "reflexo_fgts": reflexo_fgts,
            "total_reflexos": total_reflexos
        }
        
        formulas = [
            f"Valor hora = R$ {salario_base} / 220 = R$ {valor_hora:.2f}",
            f"HE 50% = R$ {valor_hora:.2f} × 1,5 = R$ {valor_he_50:.2f}",
            f"HE 100% = R$ {valor_hora:.2f} × 2,0 = R$ {valor_he_100:.2f}",
            f"Total HE = ({horas_extras_50} × R$ {valor_he_50:.2f} + {horas_extras_100} × R$ {valor_he_100:.2f}) × {meses} meses"
        ]
        
        legal_basis = [
            "Art. 7º, XVI da CF - Remuneração do trabalho extraordinário",
            "Art. 59 da CLT - Duração do trabalho",
            "Súmula 264 do TST - Reflexos das horas extras"
        ]
        
        result = CalculationResult(
            id=f"calc_{int(datetime.now().timestamp())}",
            input_id=calc_input.id,
            result_value=total_geral.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
            breakdown=self._decimal_to_float_dict(breakdown),
            formulas_used=formulas,
            legal_basis=legal_basis,
            calculation_date=datetime.now(),
            metadata={
                "meses_calculados": float(meses),
                "total_horas_50": float(horas_extras_50 * meses),
                "total_horas_100": float(horas_extras_100 * meses)
            }
        )
        
        self.calculations_history[result.id] = result
        return result
    
    def _calculate_ferias(self, calc_input: CalculationInput) -> CalculationResult:
        """Cálculo de férias"""
        params = calc_input.parameters
        
        salario = Decimal(str(params['salario']))
        dias_ferias = Decimal(str(params.get('dias_ferias', 30)))
        abono_pecuniario = params.get('abono_pecuniario', False)  # Venda de 1/3 das férias
        
        # Valor das férias
        valor_ferias = (salario / 30) * dias_ferias
        
        # 1/3 constitucional
        um_terco = valor_ferias / 3
        
        total_ferias = valor_ferias + um_terco
        
        # Abono pecuniário (venda de até 10 dias)
        valor_abono = Decimal('0')
        um_terco_abono = Decimal('0')
        
        if abono_pecuniario:
            dias_abono = min(10, int(dias_ferias / 3))  # Máximo 10 dias ou 1/3 das férias
            valor_abono = (salario / 30) * Decimal(str(dias_abono))
            um_terco_abono = valor_abono / 3
            total_ferias += valor_abono + um_terco_abono
        
        # Descontos
        base_inss = valor_ferias + um_terco + valor_abono + um_terco_abono
        desconto_inss = self._calculate_inss(base_inss)
        desconto_irrf = self._calculate_irrf(base_inss - desconto_inss)
        
        total_liquido = total_ferias - desconto_inss - desconto_irrf
        
        breakdown = {
            "valor_ferias": valor_ferias,
            "um_terco_constitucional": um_terco,
            "valor_abono_pecuniario": valor_abono,
            "um_terco_abono": um_terco_abono,
            "total_bruto": total_ferias,
            "desconto_inss": desconto_inss,
            "desconto_irrf": desconto_irrf
        }
        
        formulas = [
            f"Valor férias = (R$ {salario} / 30) × {dias_ferias} dias = R$ {valor_ferias:.2f}",
            f"1/3 constitucional = R$ {valor_ferias:.2f} / 3 = R$ {um_terco:.2f}"
        ]
        
        if abono_pecuniario:
            formulas.append(f"Abono pecuniário = (R$ {salario} / 30) × {dias_abono} dias = R$ {valor_abono:.2f}")
        
        legal_basis = [
            "Art. 7º, XVII da CF - Gozo de férias anuais remuneradas",
            "Art. 129 da CLT - Período de férias",
            "Art. 143 da CLT - Abono pecuniário"
        ]
        
        result = CalculationResult(
            id=f"calc_{int(datetime.now().timestamp())}",
            input_id=calc_input.id,
            result_value=total_liquido.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
            breakdown=self._decimal_to_float_dict(breakdown),
            formulas_used=formulas,
            legal_basis=legal_basis,
            calculation_date=datetime.now(),
            metadata={
                "dias_ferias": float(dias_ferias),
                "abono_pecuniario": abono_pecuniario,
                "dias_abono": dias_abono if abono_pecuniario else 0
            }
        )
        
        self.calculations_history[result.id] = result
        return result
    
    def _calculate_decimo_terceiro(self, calc_input: CalculationInput) -> CalculationResult:
        """Cálculo de 13º salário"""
        params = calc_input.parameters
        
        salario = Decimal(str(params['salario']))
        meses_trabalhados = Decimal(str(params.get('meses_trabalhados', 12)))
        
        # 13º proporcional
        valor_13 = (salario / 12) * meses_trabalhados
        
        # Descontos
        desconto_inss = self._calculate_inss(valor_13)
        desconto_irrf = self._calculate_irrf(valor_13 - desconto_inss)
        
        total_liquido = valor_13 - desconto_inss - desconto_irrf
        
        breakdown = {
            "valor_bruto_13": valor_13,
            "desconto_inss": desconto_inss,
            "desconto_irrf": desconto_irrf
        }
        
        formulas = [
            f"13º salário = (R$ {salario} / 12) × {meses_trabalhados} meses = R$ {valor_13:.2f}"
        ]
        
        legal_basis = [
            "Lei 4.090/62 - Gratificação de Natal",
            "Lei 4.749/65 - Regulamentação do 13º salário"
        ]
        
        result = CalculationResult(
            id=f"calc_{int(datetime.now().timestamp())}",
            input_id=calc_input.id,
            result_value=total_liquido.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
            breakdown=self._decimal_to_float_dict(breakdown),
            formulas_used=formulas,
            legal_basis=legal_basis,
            calculation_date=datetime.now(),
            metadata={
                "meses_trabalhados": float(meses_trabalhados),
                "valor_bruto": float(valor_13)
            }
        )
        
        self.calculations_history[result.id] = result
        return result
    
    def _calculate_fgts(self, calc_input: CalculationInput) -> CalculationResult:
        """Cálculo de FGTS"""
        params = calc_input.parameters
        
        salario = Decimal(str(params['salario']))
        meses = Decimal(str(params.get('meses', 12)))
        incluir_13 = params.get('incluir_13', True)
        incluir_ferias = params.get('incluir_ferias', True)
        
        # FGTS sobre salário
        fgts_salario = salario * Decimal('0.08') * meses
        
        total_fgts = fgts_salario
        
        # FGTS sobre 13º
        if incluir_13:
            fgts_13 = (salario * Decimal('0.08'))
            total_fgts += fgts_13
        
        # FGTS sobre férias + 1/3
        if incluir_ferias:
            valor_ferias = salario + (salario / 3)  # Férias + 1/3
            fgts_ferias = valor_ferias * Decimal('0.08')
            total_fgts += fgts_ferias
        
        breakdown = {
            "fgts_salario": fgts_salario,
            "fgts_13_salario": fgts_13 if incluir_13 else Decimal('0'),
            "fgts_ferias": fgts_ferias if incluir_ferias else Decimal('0'),
            "total_fgts": total_fgts
        }
        
        formulas = [
            f"FGTS salário = R$ {salario} × 8% × {meses} meses = R$ {fgts_salario:.2f}"
        ]
        
        if incluir_13:
            formulas.append(f"FGTS 13º = R$ {salario} × 8% = R$ {fgts_13:.2f}")
        
        if incluir_ferias:
            formulas.append(f"FGTS férias = (R$ {salario} + R$ {salario/3:.2f}) × 8% = R$ {fgts_ferias:.2f}")
        
        legal_basis = [
            "Lei 8.036/90 - FGTS",
            "Art. 15 da Lei 8.036/90 - Incidência do FGTS"
        ]
        
        result = CalculationResult(
            id=f"calc_{int(datetime.now().timestamp())}",
            input_id=calc_input.id,
            result_value=total_fgts.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
            breakdown=self._decimal_to_float_dict(breakdown),
            formulas_used=formulas,
            legal_basis=legal_basis,
            calculation_date=datetime.now(),
            metadata={
                "meses_calculados": float(meses),
                "incluir_13": incluir_13,
                "incluir_ferias": incluir_ferias
            }
        )
        
        self.calculations_history[result.id] = result
        return result
    
    def _calculate_civil(self, calc_input: CalculationInput) -> CalculationResult:
        """Cálculos cíveis"""
        subtype = calc_input.subtype
        
        if subtype == CivilCalculationType.DANOS_MORAIS.value:
            return self._calculate_danos_morais(calc_input)
        elif subtype == CivilCalculationType.JUROS_MORA.value:
            return self._calculate_juros_mora(calc_input)
        elif subtype == CivilCalculationType.CORRECAO_MONETARIA.value:
            return self._calculate_correcao_monetaria(calc_input)
        elif subtype == CivilCalculationType.HONORARIOS.value:
            return self._calculate_honorarios(calc_input)
        else:
            raise ValueError(f"Subtipo civil não suportado: {subtype}")
    
    def _calculate_danos_morais(self, calc_input: CalculationInput) -> CalculationResult:
        """Cálculo de danos morais"""
        params = calc_input.parameters
        
        valor_base = Decimal(str(params.get('valor_base', 0)))
        gravidade = params.get('gravidade', 'media')  # baixa, media, alta
        capacidade_economica_reu = params.get('capacidade_economica', 'media')
        repercussao = params.get('repercussao', 'local')  # local, regional, nacional
        
        # Fatores multiplicadores
        fatores_gravidade = {
            'baixa': Decimal('0.5'),
            'media': Decimal('1.0'),
            'alta': Decimal('2.0')
        }
        
        fatores_capacidade = {
            'baixa': Decimal('0.7'),
            'media': Decimal('1.0'),
            'alta': Decimal('1.5')
        }
        
        fatores_repercussao = {
            'local': Decimal('1.0'),
            'regional': Decimal('1.3'),
            'nacional': Decimal('1.8')
        }
        
        # Cálculo base (se não informado, usa salário mínimo como referência)
        if valor_base == 0:
            valor_base = Decimal('1412.00')  # Salário mínimo 2024
        
        # Aplica fatores
        fator_gravidade = fatores_gravidade.get(gravidade, Decimal('1.0'))
        fator_capacidade = fatores_capacidade.get(capacidade_economica_reu, Decimal('1.0'))
        fator_repercussao = fatores_repercussao.get(repercussao, Decimal('1.0'))
        
        valor_calculado = valor_base * fator_gravidade * fator_capacidade * fator_repercussao
        
        # Limites razoáveis (entre 1 e 500 salários mínimos)
        salario_minimo = Decimal('1412.00')
        valor_minimo = salario_minimo
        valor_maximo = salario_minimo * 500
        
        valor_final = max(valor_minimo, min(valor_calculado, valor_maximo))
        
        breakdown = {
            "valor_base": valor_base,
            "fator_gravidade": fator_gravidade,
            "fator_capacidade_economica": fator_capacidade,
            "fator_repercussao": fator_repercussao,
            "valor_calculado": valor_calculado,
            "valor_final": valor_final
        }
        
        formulas = [
            f"Valor base = R$ {valor_base}",
            f"Fator gravidade ({gravidade}) = {fator_gravidade}",
            f"Fator capacidade econômica ({capacidade_economica_reu}) = {fator_capacidade}",
            f"Fator repercussão ({repercussao}) = {fator_repercussao}",
            f"Valor = R$ {valor_base} × {fator_gravidade} × {fator_capacidade} × {fator_repercussao}"
        ]
        
        legal_basis = [
            "Art. 186 do CC - Ato ilícito",
            "Art. 927 do CC - Obrigação de reparar",
            "Art. 944 do CC - Extensão do dano",
            "Súmula 281 do STJ - Dano moral presumido"
        ]
        
        result = CalculationResult(
            id=f"calc_{int(datetime.now().timestamp())}",
            input_id=calc_input.id,
            result_value=valor_final.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
            breakdown=self._decimal_to_float_dict(breakdown),
            formulas_used=formulas,
            legal_basis=legal_basis,
            calculation_date=datetime.now(),
            metadata={
                "gravidade": gravidade,
                "capacidade_economica": capacidade_economica_reu,
                "repercussao": repercussao,
                "salarios_minimos": float(valor_final / salario_minimo)
            }
        )
        
        self.calculations_history[result.id] = result
        return result
    
    def _calculate_juros_mora(self, calc_input: CalculationInput) -> CalculationResult:
        """Cálculo de juros de mora"""
        params = calc_input.parameters
        
        valor_principal = Decimal(str(params['valor_principal']))
        data_inicial = datetime.strptime(params['data_inicial'], '%Y-%m-%d')
        data_final = datetime.strptime(params.get('data_final', datetime.now().strftime('%Y-%m-%d')), '%Y-%m-%d')
        tipo_juros = params.get('tipo_juros', 'legal')  # legal, selic, contratual
        taxa_contratual = Decimal(str(params.get('taxa_contratual', 0))) if tipo_juros == 'contratual' else None
        
        # Calcula período
        dias = (data_final - data_inicial).days
        
        if tipo_juros == 'legal':
            # 1% ao mês (12% ao ano)
            taxa_mensal = Decimal('0.01')
            meses = Decimal(str(dias)) / Decimal('30')
            juros = valor_principal * taxa_mensal * meses
            
        elif tipo_juros == 'selic':
            # Calcula SELIC acumulada (simplificado)
            juros = Decimal('0')
            current_date = data_inicial
            valor_atual = valor_principal
            
            while current_date < data_final:
                taxa_selic = self.legal_indices.get_selic_rate(current_date.year, current_date.month)
                juros_mes = valor_atual * taxa_selic
                juros += juros_mes
                valor_atual += juros_mes
                
                # Próximo mês
                if current_date.month == 12:
                    current_date = current_date.replace(year=current_date.year + 1, month=1)
                else:
                    current_date = current_date.replace(month=current_date.month + 1)
        
        elif tipo_juros == 'contratual' and taxa_contratual:
            # Taxa contratual
            meses = Decimal(str(dias)) / Decimal('30')
            juros = valor_principal * (taxa_contratual / 100) * meses
        
        else:
            juros = Decimal('0')
        
        valor_total = valor_principal + juros
        
        breakdown = {
            "valor_principal": valor_principal,
            "juros_calculados": juros,
            "valor_total": valor_total,
            "dias_periodo": dias,
            "tipo_juros": tipo_juros
        }
        
        formulas = [
            f"Período: {dias} dias ({data_inicial.strftime('%d/%m/%Y')} a {data_final.strftime('%d/%m/%Y')})",
            f"Valor principal: R$ {valor_principal}"
        ]
        
        if tipo_juros == 'legal':
            formulas.append(f"Juros legais: R$ {valor_principal} × 1% × {meses:.2f} meses = R$ {juros:.2f}")
        elif tipo_juros == 'contratual':
            formulas.append(f"Juros contratuais: R$ {valor_principal} × {taxa_contratual}% × {meses:.2f} meses = R$ {juros:.2f}")
        
        legal_basis = [
            "Art. 406 do CC - Taxa de juros",
            "Art. 407 do CC - Juros de mora",
            "Lei 9.494/97 - Juros contra a Fazenda Pública"
        ]
        
        result = CalculationResult(
            id=f"calc_{int(datetime.now().timestamp())}",
            input_id=calc_input.id,
            result_value=valor_total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
            breakdown=self._decimal_to_float_dict(breakdown),
            formulas_used=formulas,
            legal_basis=legal_basis,
            calculation_date=datetime.now(),
            metadata={
                "periodo_dias": dias,
                "tipo_juros": tipo_juros,
                "taxa_aplicada": float(taxa_contratual) if taxa_contratual else None
            }
        )
        
        self.calculations_history[result.id] = result
        return result
    
    def _calculate_correcao_monetaria(self, calc_input: CalculationInput) -> CalculationResult:
        """Cálculo de correção monetária"""
        params = calc_input.parameters
        
        valor_principal = Decimal(str(params['valor_principal']))
        data_inicial = datetime.strptime(params['data_inicial'], '%Y-%m-%d')
        data_final = datetime.strptime(params.get('data_final', datetime.now().strftime('%Y-%m-%d')), '%Y-%m-%d')
        indice = params.get('indice', 'ipca')  # ipca, igpm, inpc
        
        # Calcula correção mês a mês
        valor_corrigido = valor_principal
        total_correcao = Decimal('0')
        current_date = data_inicial
        
        breakdown_mensal = {}
        
        while current_date < data_final:
            if indice == 'ipca':
                taxa_mensal = self.legal_indices.get_ipca_rate(current_date.year, current_date.month)
            else:
                # Para outros índices, usa IPCA como padrão
                taxa_mensal = self.legal_indices.get_ipca_rate(current_date.year, current_date.month)
            
            correcao_mes = valor_corrigido * taxa_mensal
            valor_corrigido += correcao_mes
            total_correcao += correcao_mes
            
            mes_ano = f"{current_date.month:02d}/{current_date.year}"
            breakdown_mensal[mes_ano] = {
                "taxa": float(taxa_mensal * 100),
                "correcao": float(correcao_mes)
            }
            
            # Próximo mês
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
        
        breakdown = {
            "valor_principal": valor_principal,
            "total_correcao": total_correcao,
            "valor_corrigido": valor_corrigido,
            "indice_utilizado": indice.upper(),
            "breakdown_mensal": breakdown_mensal
        }
        
        formulas = [
            f"Valor principal: R$ {valor_principal}",
            f"Índice utilizado: {indice.upper()}",
            f"Período: {data_inicial.strftime('%m/%Y')} a {data_final.strftime('%m/%Y')}",
            f"Correção total: R$ {total_correcao:.2f}"
        ]
        
        legal_basis = [
            "Lei 6.899/81 - Correção monetária",
            "Lei 9.494/97 - Correção contra a Fazenda Pública",
            "Súmula 362 do STJ - Correção monetária"
        ]
        
        result = CalculationResult(
            id=f"calc_{int(datetime.now().timestamp())}",
            input_id=calc_input.id,
            result_value=valor_corrigido.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
            breakdown=self._decimal_to_float_dict(breakdown),
            formulas_used=formulas,
            legal_basis=legal_basis,
            calculation_date=datetime.now(),
            metadata={
                "indice": indice,
                "meses_correcao": len(breakdown_mensal),
                "percentual_correcao": float((total_correcao / valor_principal) * 100)
            }
        )
        
        self.calculations_history[result.id] = result
        return result
    
    def _calculate_previdenciario(self, calc_input: CalculationInput) -> CalculationResult:
        """Cálculos previdenciários (placeholder)"""
        # Implementação simplificada
        params = calc_input.parameters
        
        result = CalculationResult(
            id=f"calc_{int(datetime.now().timestamp())}",
            input_id=calc_input.id,
            result_value=Decimal('0'),
            breakdown={},
            formulas_used=["Cálculo previdenciário em desenvolvimento"],
            legal_basis=["Lei 8.213/91 - Planos de Benefícios da Previdência Social"],
            calculation_date=datetime.now(),
            metadata={"status": "em_desenvolvimento"}
        )
        
        return result
    
    def _calculate_tributario(self, calc_input: CalculationInput) -> CalculationResult:
        """Cálculos tributários (placeholder)"""
        # Implementação simplificada
        params = calc_input.parameters
        
        result = CalculationResult(
            id=f"calc_{int(datetime.now().timestamp())}",
            input_id=calc_input.id,
            result_value=Decimal('0'),
            breakdown={},
            formulas_used=["Cálculo tributário em desenvolvimento"],
            legal_basis=["CTN - Código Tributário Nacional"],
            calculation_date=datetime.now(),
            metadata={"status": "em_desenvolvimento"}
        )
        
        return result
    
    def _calculate_inss(self, base_calculo: Decimal) -> Decimal:
        """Calcula desconto de INSS"""
        tabela = self.tax_tables.get_inss_table()
        desconto = Decimal('0')
        
        for faixa_min, faixa_max, aliquota in tabela:
            if base_calculo > faixa_min:
                base_faixa = min(base_calculo, faixa_max) - faixa_min
                desconto += base_faixa * aliquota
        
        return desconto
    
    def _calculate_irrf(self, base_calculo: Decimal) -> Decimal:
        """Calcula desconto de IRRF"""
        tabela = self.tax_tables.get_irrf_table()
        
        for faixa_min, faixa_max, aliquota, deducao in tabela:
            if faixa_min <= base_calculo <= faixa_max:
                return (base_calculo * aliquota) - deducao
        
        return Decimal('0')
    
    def _decimal_to_float_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Converte Decimal para float em dicionário"""
        result = {}
        for key, value in data.items():
            if isinstance(value, Decimal):
                result[key] = float(value)
            elif isinstance(value, dict):
                result[key] = self._decimal_to_float_dict(value)
            else:
                result[key] = value
        return result
    
    def get_calculation_history(self, user_id: str = None) -> List[CalculationResult]:
        """Retorna histórico de cálculos"""
        calculations = list(self.calculations_history.values())
        
        if user_id:
            # Filtra por user_id (simplificado)
            calculations = [c for c in calculations if user_id in c.input_id]
        
        return sorted(calculations, key=lambda x: x.calculation_date, reverse=True)
    
    def get_calculation_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas de cálculos"""
        calculations = list(self.calculations_history.values())
        
        if not calculations:
            return {"message": "Nenhum cálculo realizado"}
        
        # Tipos de cálculo mais utilizados
        tipos = {}
        for calc in calculations:
            # Extrai tipo do metadata ou input_id
            tipo = calc.metadata.get('tipo', 'Desconhecido')
            tipos[tipo] = tipos.get(tipo, 0) + 1
        
        # Valor médio dos cálculos
        valores = [float(c.result_value) for c in calculations if c.result_value > 0]
        valor_medio = sum(valores) / len(valores) if valores else 0
        
        return {
            "total_calculos": len(calculations),
            "tipos_mais_utilizados": tipos,
            "valor_medio_calculos": round(valor_medio, 2),
            "maior_valor": max(valores) if valores else 0,
            "menor_valor": min(valores) if valores else 0
        }

def main():
    """Função principal para demonstração"""
    print("=== Calculadora Jurídica Avançada - Versão Melhorada ===")
    
    # Cria instância da calculadora
    calculator = EnhancedLegalCalculator()
    
    # Exemplo 1: Cálculo de rescisão
    print("\n--- Cálculo de Rescisão ---")
    calc_input_rescisao = CalculationInput(
        id="calc_rescisao_001",
        calculation_type=CalculationType.TRABALHISTA,
        subtype=WorkerCalculationType.RESCISAO.value,
        parameters={
            "salario": 3000.00,
            "data_admissao": "2022-01-15",
            "data_demissao": "2024-09-15",
            "tipo_rescisao": "sem_justa_causa",
            "aviso_previo_trabalhado": False
        },
        user_id="usuario_teste",
        timestamp=datetime.now()
    )
    
    result_rescisao = calculator.calculate(calc_input_rescisao)
    print(f"Valor total da rescisão: R$ {result_rescisao.result_value}")
    print(f"Tempo de serviço: {result_rescisao.metadata['tempo_servico_anos']} anos")
    print(f"Verbas principais: Saldo, 13º, Férias, Aviso Prévio, Multa FGTS")
    
    # Exemplo 2: Cálculo de horas extras
    print("\n--- Cálculo de Horas Extras ---")
    calc_input_he = CalculationInput(
        id="calc_he_001",
        calculation_type=CalculationType.TRABALHISTA,
        subtype=WorkerCalculationType.HORAS_EXTRAS.value,
        parameters={
            "salario_base": 2500.00,
            "horas_extras_50": 20,  # 20 horas extras 50% por mês
            "horas_extras_100": 5,  # 5 horas extras 100% por mês
            "meses": 12
        },
        user_id="usuario_teste",
        timestamp=datetime.now()
    )
    
    result_he = calculator.calculate(calc_input_he)
    print(f"Total horas extras + reflexos: R$ {result_he.result_value}")
    print(f"Horas 50%: {result_he.metadata['total_horas_50']}")
    print(f"Horas 100%: {result_he.metadata['total_horas_100']}")
    
    # Exemplo 3: Cálculo de danos morais
    print("\n--- Cálculo de Danos Morais ---")
    calc_input_danos = CalculationInput(
        id="calc_danos_001",
        calculation_type=CalculationType.CIVIL,
        subtype=CivilCalculationType.DANOS_MORAIS.value,
        parameters={
            "valor_base": 5000.00,
            "gravidade": "alta",
            "capacidade_economica": "alta",
            "repercussao": "regional"
        },
        user_id="usuario_teste",
        timestamp=datetime.now()
    )
    
    result_danos = calculator.calculate(calc_input_danos)
    print(f"Valor sugerido para danos morais: R$ {result_danos.result_value}")
    print(f"Equivale a {result_danos.metadata['salarios_minimos']:.1f} salários mínimos")
    
    # Exemplo 4: Cálculo de juros de mora
    print("\n--- Cálculo de Juros de Mora ---")
    calc_input_juros = CalculationInput(
        id="calc_juros_001",
        calculation_type=CalculationType.CIVIL,
        subtype=CivilCalculationType.JUROS_MORA.value,
        parameters={
            "valor_principal": 10000.00,
            "data_inicial": "2023-01-01",
            "data_final": "2024-09-13",
            "tipo_juros": "legal"
        },
        user_id="usuario_teste",
        timestamp=datetime.now()
    )
    
    result_juros = calculator.calculate(calc_input_juros)
    print(f"Valor com juros: R$ {result_juros.result_value}")
    print(f"Período: {result_juros.metadata['periodo_dias']} dias")
    print(f"Juros calculados: R$ {result_juros.breakdown['juros_calculados']}")
    
    # Estatísticas
    stats = calculator.get_calculation_statistics()
    print(f"\n--- Estatísticas ---")
    print(f"Total de cálculos: {stats['total_calculos']}")
    print(f"Valor médio: R$ {stats['valor_medio_calculos']}")
    print(f"Maior valor: R$ {stats['maior_valor']}")
    
    return calculator

if __name__ == "__main__":
    main()

