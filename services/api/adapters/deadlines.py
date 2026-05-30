from datetime import date
from functools import lru_cache

import services.api.bootstrap  # noqa: F401

from deadline_manager import CourtType, DeadlineCalculator, DeadlineType

_ENUM_MAP = {
    "contestacao": DeadlineType.CONTESTACAO,
    "recurso": DeadlineType.RECURSO,
    "replicas": DeadlineType.REPLICAS,
    "embargos": DeadlineType.EMBARGOS,
    "cumprimento_sentenca": DeadlineType.CUMPRIMENTO_SENTENCA,
    "manifestacao": DeadlineType.MANIFESTACAO,
    "juntada_documentos": DeadlineType.JUNTADA_DOCUMENTOS,
    "pagamento": DeadlineType.PAGAMENTO,
}

_COURT_MAP = {
    "estadual": CourtType.ESTADUAL,
    "federal": CourtType.FEDERAL,
    "trabalhista": CourtType.TRABALHISTA,
    "eleitoral": CourtType.ELEITORAL,
    "militar": CourtType.MILITAR,
    "superior": CourtType.SUPERIOR,
}


@lru_cache(maxsize=1)
def get_calculator() -> DeadlineCalculator:
    return DeadlineCalculator()


def calculate_deadline(
    event_date: date,
    deadline_type: str,
    court_type: str = "estadual",
    custom_days: int | None = None,
) -> dict:
    dt = _ENUM_MAP.get(deadline_type.lower())
    if dt is None:
        raise ValueError(f"Tipo de prazo inválido: {deadline_type}")

    court = _COURT_MAP.get(court_type.lower(), CourtType.ESTADUAL)
    result = get_calculator().calculate_deadline(event_date, dt, court, custom_days)

    return {
        "base_date": result.base_date.isoformat(),
        "deadline_type": deadline_type,
        "court_type": court_type,
        "calculated_date": result.calculated_date.isoformat(),
        "business_days": result.business_days,
        "excluded_dates": [d.isoformat() for d in result.excluded_dates],
        "calculation_details": result.calculation_details,
    }
