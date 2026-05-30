from datetime import datetime
from decimal import Decimal
from functools import lru_cache
from uuid import uuid4

import services.api.bootstrap  # noqa: F401

from enhanced_legal_calculator import (
    CalculationInput,
    CalculationType,
    CivilCalculationType,
    EnhancedLegalCalculator,
    WorkerCalculationType,
)

_CALC_MAP = {
    ("trabalhista", "rescisao"): (CalculationType.TRABALHISTA, WorkerCalculationType.RESCISAO.value),
    ("civil", "danos_morais"): (CalculationType.CIVIL, CivilCalculationType.DANOS_MORAIS.value),
    ("civil", "correcao_monetaria"): (CalculationType.CIVIL, CivilCalculationType.CORRECAO_MONETARIA.value),
    ("civil", "honorarios"): (CalculationType.CIVIL, CivilCalculationType.HONORARIOS.value),
}


@lru_cache(maxsize=1)
def get_calculator() -> EnhancedLegalCalculator:
    return EnhancedLegalCalculator()


def run_calculation(area: str, subtype: str, parameters: dict, user_id: str = "api") -> dict:
    key = (area.lower(), subtype.lower())
    if key not in _CALC_MAP:
        raise ValueError(f"Cálculo não suportado: {area}/{subtype}")

    calc_type, sub = _CALC_MAP[key]
    calc_input = CalculationInput(
        id=str(uuid4()),
        calculation_type=calc_type,
        subtype=sub,
        parameters=parameters,
        user_id=user_id,
        timestamp=datetime.now(),
    )
    result = get_calculator().calculate(calc_input)

    return {
        "id": result.id,
        "result_value": str(result.result_value),
        "breakdown": result.breakdown,
        "formulas_used": result.formulas_used,
        "legal_basis": result.legal_basis,
        "calculation_date": result.calculation_date.isoformat(),
        "metadata": result.metadata,
    }
