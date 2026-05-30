"""
Funcionalidades Avançadas da Calculadora Jurídica
Implementa novos tipos de cálculo, validação cruzada e histórico
"""

import json
import math
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import numpy as np
from decimal import Decimal, ROUND_HALF_UP

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CalculationType(Enum):
    """Tipos de cálculo jurídico"""
    TRABALHISTA_RESCISAO = "Rescisão Trabalhista"
    TRABALHISTA_HORAS_EXTRAS = "Horas Extras"
    CIVIL_DANOS_MORAIS = "Danos Morais"
    CIVIL_JUROS_CORRECAO = "Juros e Correção Monetária"
    TRIBUTARIO_MULTA = "Multa Tributária"
    PREVIDENCIARIO_BENEFICIO = "Benefício Previdenciário"
    CONSUMIDOR_RESTITUICAO = "Restituição em Dobro"
    EXECUCAO_HONORARIOS = "Honorários Advocatícios"
    ALIMENTOS_PENSAO = "Pensão Alimentícia"
    INVENTARIO_MEACAO = "Meação e Herança"

class ValidationLevel(Enum):
    """Níveis de validação"""
    BASIC = "Básico"
    INTERMEDIATE = "Intermediário"
    COMPREHENSIVE = "Abrangente"
    EXPERT = "Especialista"

@dataclass
class CalculationInput:
    """Entrada para cálculo"""
    calculation_type: CalculationType
    parameters: Dict[str, Any]
    validation_level: ValidationLevel
    user_id: str
    timestamp: datetime

@dataclass
class CalculationResult:
    """Resultado de cálculo"""
    id: str
    calculation_type: CalculationType
    input_parameters: Dict[str, Any]
    result_value: Decimal
    breakdown: Dict[str, Decimal]
    validation_status: str
    confidence_score: float
    warnings: List[str]
    recommendations: List[str]
    legal_basis: List[str]
    timestamp: datetime
    calculation_time: float

@dataclass
class ValidationResult:
    """Resultado de validação"""
    is_valid: bool
    confidence: float
    issues: List[str]
    suggestions: List[str]
    cross_validation: Dict[str, Any]

class LegalParametersDatabase:
    """Base de dados de parâmetros legais"""
    
    def __init__(self):
        self.parameters = self._load_legal_parameters()
        self.indices = self._load_economic_indices()
        
    def _load_legal_parameters(self) -> Dict[str, Dict[str, Any]]:
        """Carrega parâmetros legais atualizados"""
        return {
            "trabalhista": {
                "salario_minimo": Decimal("1412.00"),  # 2024
                "fator_previdenciario": Decimal("0.08"),
                "adicional_noturno": Decimal("0.20"),
                "adicional_periculosidade": Decimal("0.30"),
                "adicional_insalubridade": {
                    "minimo": Decimal("0.10"),
                    "medio": Decimal("0.20"),
                    "maximo": Decimal("0.40")
                },
                "aviso_previo_base": 30,  # dias
                "aviso_previo_adicional": 3,  # dias por ano
                "fgts_aliquota": Decimal("0.08"),
                "fgts_multa": Decimal("0.40")
            },
            "civil": {
                "juros_mora_civil": Decimal("0.01"),  # 1% ao mês
                "juros_mora_fazenda": Decimal("0.005"),  # 0.5% ao mês
                "honorarios_minimo": Decimal("0.10"),
                "honorarios_maximo": Decimal("0.20"),
                "danos_morais_minimo": Decimal("1000.00"),
                "danos_morais_maximo": Decimal("50000.00")
            },
            "tributario": {
                "selic_anual": Decimal("0.1175"),  # 11.75% ao ano
                "multa_atraso": Decimal("0.02"),  # 2%
                "multa_sonegacao": Decimal("1.50"),  # 150%
                "juros_parcelamento": Decimal("0.01")  # 1% ao mês
            },
            "previdenciario": {
                "teto_beneficio": Decimal("7786.02"),  # 2024
                "salario_beneficio_minimo": Decimal("1412.00"),
                "fator_85_95": True,  # Regra 85/95
                "idade_minima_homem": 65,
                "idade_minima_mulher": 62
            }
        }
    
    def _load_economic_indices(self) -> Dict[str, List[Dict[str, Any]]]:
        """Carrega índices econômicos"""
        return {
            "ipca": [
                {"date": "2024-01", "value": Decimal("0.0042")},
                {"date": "2024-02", "value": Decimal("0.0083")},
                {"date": "2024-03", "value": Decimal("0.0016")},
                {"date": "2024-04", "value": Decimal("0.0038")},
                {"date": "2024-05", "value": Decimal("0.0046")},
                {"date": "2024-06", "value": Decimal("0.0021")},
                {"date": "2024-07", "value": Decimal("0.0038")},
                {"date": "2024-08", "value": Decimal("0.0002")},
                {"date": "2024-09", "value": Decimal("0.0044")}
            ],
            "inpc": [
                {"date": "2024-01", "value": Decimal("0.0045")},
                {"date": "2024-02", "value": Decimal("0.0089")},
                {"date": "2024-03", "value": Decimal("0.0018")},
                {"date": "2024-04", "value": Decimal("0.0040")},
                {"date": "2024-05", "value": Decimal("0.0048")},
                {"date": "2024-06", "value": Decimal("0.0023")},
                {"date": "2024-07", "value": Decimal("0.0040")},
                {"date": "2024-08", "value": Decimal("0.0003")},
                {"date": "2024-09", "value": Decimal("0.0046")}
            ]
        }

class AdvancedCalculationEngine:
    """Motor avançado de cálculos jurídicos"""
    
    def __init__(self):
        self.legal_db = LegalParametersDatabase()
        self.calculation_history = []
        self.validators = self._initialize_validators()
        
    def _initialize_validators(self) -> Dict[str, Any]:
        """Inicializa validadores específicos"""
        return {
            # Validadores serão implementados conforme necessário
        }
    
    def calculate_advanced(self, calc_input: CalculationInput) -> CalculationResult:
        """Executa cálculo avançado com validação"""
        start_time = datetime.now()
        
        # Valida parâmetros de entrada
        validation = self._validate_input_parameters(calc_input)
        
        if not validation.is_valid and calc_input.validation_level != ValidationLevel.BASIC:
            raise ValueError(f"Parâmetros inválidos: {validation.issues}")
        
        # Executa cálculo específico
        result_value, breakdown = self._execute_calculation(calc_input)
        
        # Validação cruzada
        cross_validation = self._perform_cross_validation(calc_input, result_value)
        
        # Gera recomendações
        recommendations = self._generate_recommendations(calc_input, result_value)
        
        # Base legal
        legal_basis = self._get_legal_basis(calc_input.calculation_type)
        
        # Calcula tempo de execução
        calculation_time = (datetime.now() - start_time).total_seconds()
        
        # Cria resultado
        result = CalculationResult(
            id=f"calc_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.calculation_history)}",
            calculation_type=calc_input.calculation_type,
            input_parameters=calc_input.parameters,
            result_value=result_value,
            breakdown=breakdown,
            validation_status="VALID" if validation.is_valid else "WARNING",
            confidence_score=validation.confidence,
            warnings=validation.issues,
            recommendations=recommendations,
            legal_basis=legal_basis,
            timestamp=calc_input.timestamp,
            calculation_time=calculation_time
        )
        
        # Adiciona ao histórico
        self.calculation_history.append(result)
        
        logger.info(f"Cálculo executado: {calc_input.calculation_type.value} - R$ {result_value}")
        
        return result
    
    def _validate_input_parameters(self, calc_input: CalculationInput) -> ValidationResult:
        """Valida parâmetros de entrada"""
        issues = []
        suggestions = []
        confidence = 1.0
        
        calc_type = calc_input.calculation_type
        params = calc_input.parameters
        
        # Validação específica por tipo
        if calc_type == CalculationType.TRABALHISTA_RESCISAO:
            try:
                salario = float(params.get("salario", 0))
                if salario <= 0:
                    issues.append("Salário deve ser maior que zero")
                    confidence -= 0.3
            except (ValueError, TypeError):
                issues.append("Salário deve ser um valor numérico válido")
                confidence -= 0.3
            
            try:
                tempo_servico = int(params.get("tempo_servico_meses", 0))
                if tempo_servico < 0:
                    issues.append("Tempo de serviço deve ser positivo")
                    confidence -= 0.2
            except (ValueError, TypeError):
                issues.append("Tempo de serviço deve ser um número inteiro")
                confidence -= 0.2
            
            try:
                salario_val = float(params.get("salario", 0))
                if salario_val < float(self.legal_db.parameters["trabalhista"]["salario_minimo"]):
                    suggestions.append("Salário abaixo do mínimo legal")
                    confidence -= 0.1
            except (ValueError, TypeError):
                pass
        
        elif calc_type == CalculationType.CIVIL_DANOS_MORAIS:
            if "gravidade" not in params:
                issues.append("Nível de gravidade deve ser especificado")
                confidence -= 0.4
            
            if "renda_vitima" not in params:
                suggestions.append("Renda da vítima ajuda na quantificação")
                confidence -= 0.1
        
        # Validação de datas
        for key, value in params.items():
            if "data" in key.lower() and isinstance(value, str):
                try:
                    datetime.strptime(value, "%Y-%m-%d")
                except ValueError:
                    issues.append(f"Data inválida: {key}")
                    confidence -= 0.2
        
        return ValidationResult(
            is_valid=len(issues) == 0,
            confidence=max(confidence, 0.0),
            issues=issues,
            suggestions=suggestions,
            cross_validation={}
        )
    
    def _execute_calculation(self, calc_input: CalculationInput) -> Tuple[Decimal, Dict[str, Decimal]]:
        """Executa o cálculo específico"""
        calc_type = calc_input.calculation_type
        params = calc_input.parameters
        
        if calc_type == CalculationType.TRABALHISTA_RESCISAO:
            return self._calculate_rescisao_trabalhista(params)
        elif calc_type == CalculationType.TRABALHISTA_HORAS_EXTRAS:
            return self._calculate_horas_extras(params)
        elif calc_type == CalculationType.CIVIL_DANOS_MORAIS:
            return self._calculate_danos_morais(params)
        elif calc_type == CalculationType.CIVIL_JUROS_CORRECAO:
            return self._calculate_juros_correcao(params)
        elif calc_type == CalculationType.TRIBUTARIO_MULTA:
            return self._calculate_multa_tributaria(params)
        elif calc_type == CalculationType.EXECUCAO_HONORARIOS:
            return self._calculate_honorarios_advocaticios(params)
        else:
            raise ValueError(f"Tipo de cálculo não implementado: {calc_type}")
    
    def _calculate_rescisao_trabalhista(self, params: Dict[str, Any]) -> Tuple[Decimal, Dict[str, Decimal]]:
        """Calcula rescisão trabalhista completa"""
        salario = Decimal(str(params["salario"]))
        tempo_servico_meses = int(params["tempo_servico_meses"])
        tipo_rescisao = params.get("tipo_rescisao", "sem_justa_causa")
        
        breakdown = {}
        
        # Saldo de salário (proporcional)
        dias_trabalhados = int(params.get("dias_trabalhados_mes", 30))
        saldo_salario = (salario / 30) * dias_trabalhados
        breakdown["saldo_salario"] = saldo_salario
        
        # Aviso prévio
        if tipo_rescisao == "sem_justa_causa":
            anos_servico = tempo_servico_meses // 12
            dias_aviso = 30 + (anos_servico * 3)
            aviso_previo = (salario / 30) * min(dias_aviso, 90)
            breakdown["aviso_previo"] = aviso_previo
        else:
            breakdown["aviso_previo"] = Decimal("0")
        
        # 13º salário proporcional
        meses_13 = tempo_servico_meses % 12
        if params.get("dias_trabalhados_mes", 30) >= 15:
            meses_13 += 1
        decimo_terceiro = (salario * meses_13) / 12
        breakdown["decimo_terceiro"] = decimo_terceiro
        
        # Férias proporcionais + 1/3
        meses_ferias = tempo_servico_meses % 12
        if params.get("dias_trabalhados_mes", 30) >= 15:
            meses_ferias += 1
        ferias_proporcionais = (salario * meses_ferias) / 12
        terco_ferias = ferias_proporcionais / 3
        breakdown["ferias_proporcionais"] = ferias_proporcionais
        breakdown["terco_ferias"] = terco_ferias
        
        # FGTS + Multa (se aplicável)
        fgts_depositos = salario * tempo_servico_meses * self.legal_db.parameters["trabalhista"]["fgts_aliquota"]
        breakdown["fgts_depositos"] = fgts_depositos
        
        if tipo_rescisao == "sem_justa_causa":
            multa_fgts = fgts_depositos * self.legal_db.parameters["trabalhista"]["fgts_multa"]
            breakdown["multa_fgts"] = multa_fgts
        else:
            breakdown["multa_fgts"] = Decimal("0")
        
        # Seguro desemprego (informativo, não valor)
        breakdown["seguro_desemprego"] = Decimal("0")  # Não é pago pelo empregador
        
        # Total
        total = sum(breakdown.values())
        
        return total, breakdown
    
    def _calculate_horas_extras(self, params: Dict[str, Any]) -> Tuple[Decimal, Dict[str, Decimal]]:
        """Calcula horas extras"""
        salario_hora = Decimal(str(params["salario_hora"]))
        horas_extras = Decimal(str(params["horas_extras"]))
        percentual_adicional = Decimal(str(params.get("percentual_adicional", "50"))) / 100
        
        breakdown = {}
        
        # Valor da hora extra
        valor_hora_extra = salario_hora * (1 + percentual_adicional)
        breakdown["valor_hora_extra"] = valor_hora_extra
        
        # Total horas extras
        total_horas_extras = valor_hora_extra * horas_extras
        breakdown["total_horas_extras"] = total_horas_extras
        
        # Reflexos
        reflexo_13 = total_horas_extras / 12
        reflexo_ferias = total_horas_extras / 12
        reflexo_fgts = total_horas_extras * self.legal_db.parameters["trabalhista"]["fgts_aliquota"]
        
        breakdown["reflexo_13_salario"] = reflexo_13
        breakdown["reflexo_ferias"] = reflexo_ferias
        breakdown["reflexo_fgts"] = reflexo_fgts
        
        total = total_horas_extras + reflexo_13 + reflexo_ferias + reflexo_fgts
        
        return total, breakdown
    
    def _calculate_danos_morais(self, params: Dict[str, Any]) -> Tuple[Decimal, Dict[str, Decimal]]:
        """Calcula danos morais"""
        gravidade = params.get("gravidade", "media")  # baixa, media, alta
        renda_vitima = Decimal(str(params.get("renda_vitima", "5000")))
        capacidade_pagador = Decimal(str(params.get("capacidade_pagador", "100000")))
        
        breakdown = {}
        
        # Base de cálculo por gravidade
        multiplicadores = {
            "baixa": Decimal("3"),
            "media": Decimal("5"),
            "alta": Decimal("10"),
            "gravissima": Decimal("20")
        }
        
        multiplicador = multiplicadores.get(gravidade, Decimal("5"))
        
        # Cálculo base
        valor_base = renda_vitima * multiplicador
        breakdown["valor_base"] = valor_base
        
        # Ajuste por capacidade econômica
        if capacidade_pagador > 50000:
            fator_capacidade = min(Decimal("2.0"), capacidade_pagador / 50000)
            ajuste_capacidade = valor_base * (fator_capacidade - 1) * Decimal("0.5")
            breakdown["ajuste_capacidade"] = ajuste_capacidade
        else:
            breakdown["ajuste_capacidade"] = Decimal("0")
        
        # Limites legais
        valor_final = valor_base + breakdown["ajuste_capacidade"]
        
        # Aplica limites mínimo e máximo
        min_valor = self.legal_db.parameters["civil"]["danos_morais_minimo"]
        max_valor = self.legal_db.parameters["civil"]["danos_morais_maximo"]
        
        valor_final = max(min_valor, min(valor_final, max_valor))
        breakdown["valor_final"] = valor_final
        
        return valor_final, breakdown
    
    def _calculate_juros_correcao(self, params: Dict[str, Any]) -> Tuple[Decimal, Dict[str, Decimal]]:
        """Calcula juros e correção monetária"""
        valor_principal = Decimal(str(params["valor_principal"]))
        data_inicial = datetime.strptime(params["data_inicial"], "%Y-%m-%d")
        data_final = datetime.strptime(params.get("data_final", datetime.now().strftime("%Y-%m-%d")), "%Y-%m-%d")
        tipo_devedor = params.get("tipo_devedor", "particular")  # particular, fazenda_publica
        
        breakdown = {}
        breakdown["valor_principal"] = valor_principal
        
        # Calcula correção monetária (IPCA)
        correcao_monetaria = self._calculate_monetary_correction(valor_principal, data_inicial, data_final)
        breakdown["correcao_monetaria"] = correcao_monetaria
        
        # Calcula juros de mora
        if tipo_devedor == "fazenda_publica":
            taxa_juros = self.legal_db.parameters["civil"]["juros_mora_fazenda"]
        else:
            taxa_juros = self.legal_db.parameters["civil"]["juros_mora_civil"]
        
        meses_atraso = ((data_final.year - data_inicial.year) * 12 + 
                       (data_final.month - data_inicial.month))
        
        juros_mora = valor_principal * taxa_juros * meses_atraso
        breakdown["juros_mora"] = juros_mora
        
        total = valor_principal + correcao_monetaria + juros_mora
        
        return total, breakdown
    
    def _calculate_monetary_correction(self, valor: Decimal, data_inicial: datetime, 
                                     data_final: datetime) -> Decimal:
        """Calcula correção monetária pelo IPCA"""
        fator_correcao = Decimal("1.0")
        
        # Aplica índices IPCA disponíveis
        for indice in self.legal_db.indices["ipca"]:
            indice_date = datetime.strptime(indice["date"], "%Y-%m")
            if data_inicial <= indice_date <= data_final:
                fator_correcao *= (1 + indice["value"])
        
        correcao = valor * (fator_correcao - 1)
        return correcao
    
    def _calculate_multa_tributaria(self, params: Dict[str, Any]) -> Tuple[Decimal, Dict[str, Decimal]]:
        """Calcula multa tributária"""
        valor_tributo = Decimal(str(params["valor_tributo"]))
        tipo_infracacao = params.get("tipo_infracacao", "atraso")  # atraso, sonegacao
        meses_atraso = int(params.get("meses_atraso", 1))
        
        breakdown = {}
        breakdown["valor_tributo"] = valor_tributo
        
        if tipo_infracacao == "sonegacao":
            multa = valor_tributo * self.legal_db.parameters["tributario"]["multa_sonegacao"]
            breakdown["multa_sonegacao"] = multa
        else:
            multa = valor_tributo * self.legal_db.parameters["tributario"]["multa_atraso"]
            breakdown["multa_atraso"] = multa
        
        # Juros SELIC
        taxa_selic_mensal = self.legal_db.parameters["tributario"]["selic_anual"] / 12
        juros_selic = valor_tributo * taxa_selic_mensal * meses_atraso
        breakdown["juros_selic"] = juros_selic
        
        total = valor_tributo + multa + juros_selic
        
        return total, breakdown
    
    def _calculate_honorarios_advocaticios(self, params: Dict[str, Any]) -> Tuple[Decimal, Dict[str, Decimal]]:
        """Calcula honorários advocatícios"""
        valor_causa = Decimal(str(params["valor_causa"]))
        percentual = Decimal(str(params.get("percentual", "15"))) / 100
        tipo_acao = params.get("tipo_acao", "conhecimento")
        
        breakdown = {}
        breakdown["valor_causa"] = valor_causa
        
        # Limites legais
        min_perc = self.legal_db.parameters["civil"]["honorarios_minimo"]
        max_perc = self.legal_db.parameters["civil"]["honorarios_maximo"]
        
        percentual = max(min_perc, min(percentual, max_perc))
        breakdown["percentual_aplicado"] = percentual * 100
        
        honorarios = valor_causa * percentual
        breakdown["honorarios_calculados"] = honorarios
        
        # Ajustes por tipo de ação
        if tipo_acao == "execucao":
            honorarios *= Decimal("1.5")  # Majoração para execução
            breakdown["majoracao_execucao"] = honorarios - breakdown["honorarios_calculados"]
        
        return honorarios, breakdown
    
    def _perform_cross_validation(self, calc_input: CalculationInput, 
                                 result_value: Decimal) -> Dict[str, Any]:
        """Realiza validação cruzada"""
        cross_validation = {}
        
        # Validação por método alternativo
        if calc_input.calculation_type == CalculationType.CIVIL_DANOS_MORAIS:
            # Método alternativo: múltiplos do salário mínimo
            salario_minimo = self.legal_db.parameters["trabalhista"]["salario_minimo"]
            multiplos_sm = result_value / salario_minimo
            cross_validation["multiplos_salario_minimo"] = float(multiplos_sm)
            
            if multiplos_sm < 1 or multiplos_sm > 50:
                cross_validation["warning"] = "Valor fora da faixa usual (1-50 salários mínimos)"
        
        # Validação de razoabilidade
        if result_value < 0:
            cross_validation["error"] = "Resultado negativo não é válido"
        elif result_value > 1000000:  # 1 milhão
            cross_validation["warning"] = "Valor muito alto, revisar parâmetros"
        
        return cross_validation
    
    def _generate_recommendations(self, calc_input: CalculationInput, 
                                result_value: Decimal) -> List[str]:
        """Gera recomendações baseadas no cálculo"""
        recommendations = []
        
        calc_type = calc_input.calculation_type
        
        if calc_type == CalculationType.TRABALHISTA_RESCISAO:
            recommendations.append("Verificar se há verbas em atraso não computadas")
            recommendations.append("Considerar adicionar correção monetária se aplicável")
            
        elif calc_type == CalculationType.CIVIL_DANOS_MORAIS:
            recommendations.append("Fundamentar o valor com jurisprudência similar")
            recommendations.append("Considerar peculiaridades do caso concreto")
            
        elif calc_type == CalculationType.CIVIL_JUROS_CORRECAO:
            recommendations.append("Verificar se a taxa de juros está correta para o tipo de devedor")
            recommendations.append("Confirmar índice de correção aplicável")
        
        return recommendations
    
    def _get_legal_basis(self, calc_type: CalculationType) -> List[str]:
        """Retorna base legal para o tipo de cálculo"""
        legal_basis = {
            CalculationType.TRABALHISTA_RESCISAO: [
                "CLT, art. 477 e seguintes",
                "Lei 8.036/90 (FGTS)",
                "Súmula 261 do TST"
            ],
            CalculationType.CIVIL_DANOS_MORAIS: [
                "CC, art. 186 e 927",
                "CF, art. 5º, V e X",
                "Súmula 281 do STJ"
            ],
            CalculationType.CIVIL_JUROS_CORRECAO: [
                "CC, art. 404 e 405",
                "Lei 6.899/81",
                "Súmula 54 do STJ"
            ],
            CalculationType.EXECUCAO_HONORARIOS: [
                "CPC, art. 85",
                "Súmula 111 do STJ"
            ]
        }
        
        return legal_basis.get(calc_type, ["Legislação aplicável ao caso"])
    
    def get_calculation_history(self, user_id: str = None, 
                              calc_type: CalculationType = None) -> List[CalculationResult]:
        """Retorna histórico de cálculos"""
        history = self.calculation_history
        
        if user_id:
            history = [c for c in history if c.input_parameters.get("user_id") == user_id]
        
        if calc_type:
            history = [c for c in history if c.calculation_type == calc_type]
        
        return sorted(history, key=lambda x: x.timestamp, reverse=True)
    
    def get_calculation_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas dos cálculos"""
        if not self.calculation_history:
            return {"message": "Nenhum cálculo realizado ainda"}
        
        # Contagem por tipo
        type_counts = {}
        for calc in self.calculation_history:
            calc_type = calc.calculation_type.value
            type_counts[calc_type] = type_counts.get(calc_type, 0) + 1
        
        # Valores médios
        total_values = [float(calc.result_value) for calc in self.calculation_history]
        avg_value = sum(total_values) / len(total_values)
        
        # Tempo médio de cálculo
        avg_time = sum(calc.calculation_time for calc in self.calculation_history) / len(self.calculation_history)
        
        return {
            "total_calculations": len(self.calculation_history),
            "calculations_by_type": type_counts,
            "average_value": round(avg_value, 2),
            "average_calculation_time": round(avg_time, 4),
            "most_used_type": max(type_counts.items(), key=lambda x: x[1])[0] if type_counts else None
        }

def main():
    """Função principal para demonstração"""
    print("=== Funcionalidades Avançadas da Calculadora Jurídica ===")
    
    # Cria motor de cálculo avançado
    calc_engine = AdvancedCalculationEngine()
    
    # Exemplos de cálculos
    print("\n--- Exemplo 1: Rescisão Trabalhista ---")
    calc_input_1 = CalculationInput(
        calculation_type=CalculationType.TRABALHISTA_RESCISAO,
        parameters={
            "salario": "3000.00",
            "tempo_servico_meses": 24,
            "tipo_rescisao": "sem_justa_causa",
            "dias_trabalhados_mes": 30
        },
        validation_level=ValidationLevel.COMPREHENSIVE,
        user_id="user123",
        timestamp=datetime.now()
    )
    
    resultado_1 = calc_engine.calculate_advanced(calc_input_1)
    print(f"Valor total: R$ {resultado_1.result_value}")
    print(f"Confiança: {resultado_1.confidence_score:.2f}")
    print("Breakdown:")
    for item, valor in resultado_1.breakdown.items():
        print(f"  {item}: R$ {valor}")
    
    print("\n--- Exemplo 2: Danos Morais ---")
    calc_input_2 = CalculationInput(
        calculation_type=CalculationType.CIVIL_DANOS_MORAIS,
        parameters={
            "gravidade": "media",
            "renda_vitima": "5000.00",
            "capacidade_pagador": "200000.00"
        },
        validation_level=ValidationLevel.INTERMEDIATE,
        user_id="user123",
        timestamp=datetime.now()
    )
    
    resultado_2 = calc_engine.calculate_advanced(calc_input_2)
    print(f"Valor sugerido: R$ {resultado_2.result_value}")
    print(f"Recomendações: {resultado_2.recommendations}")
    
    print("\n--- Exemplo 3: Juros e Correção ---")
    calc_input_3 = CalculationInput(
        calculation_type=CalculationType.CIVIL_JUROS_CORRECAO,
        parameters={
            "valor_principal": "10000.00",
            "data_inicial": "2023-01-01",
            "data_final": "2024-09-14",
            "tipo_devedor": "particular"
        },
        validation_level=ValidationLevel.BASIC,
        user_id="user456",
        timestamp=datetime.now()
    )
    
    resultado_3 = calc_engine.calculate_advanced(calc_input_3)
    print(f"Valor atualizado: R$ {resultado_3.result_value}")
    print("Breakdown:")
    for item, valor in resultado_3.breakdown.items():
        print(f"  {item}: R$ {valor}")
    
    # Estatísticas
    print("\n--- Estatísticas dos Cálculos ---")
    stats = calc_engine.get_calculation_statistics()
    print(f"Total de cálculos: {stats['total_calculations']}")
    print(f"Valor médio: R$ {stats['average_value']}")
    print(f"Tempo médio: {stats['average_calculation_time']}s")
    print(f"Tipo mais usado: {stats['most_used_type']}")
    
    return calc_engine

if __name__ == "__main__":
    main()

