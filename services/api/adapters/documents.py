from functools import lru_cache

import services.api.bootstrap  # noqa: F401 — sys.path

from enhanced_document_analyzer import EnhancedDocumentAnalyzer

from legal_core.serializers import analysis_to_api_payload


@lru_cache(maxsize=1)
def get_analyzer() -> EnhancedDocumentAnalyzer:
    return EnhancedDocumentAnalyzer()


def analyze_document_text(
    text: str,
    legal_area: str | None = None,
    enhance_with_gemini: bool = False,
) -> dict:
    analysis = get_analyzer().analyze_document(text)
    payload = analysis_to_api_payload(analysis, legal_area=legal_area, source_text=text)

    if enhance_with_gemini:
        from ai_provider.gemini import enhance_document_analysis, is_gemini_available

        if not is_gemini_available():
            raise ValueError(
                "GEMINI_API_KEY não configurada no servidor. "
                "Use análise local ou configure a chave."
            )
        payload = enhance_document_analysis(text, payload, legal_area)

    return payload
