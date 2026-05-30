from __future__ import annotations

from functools import lru_cache
from typing import Any

import services.api.bootstrap  # noqa: F401

from enhanced_virtual_assistant import EnhancedVirtualAssistant, ResponseStyle

DISCLAIMER = (
    "Orientação de apoio; não substitui parecer jurídico nem advogado habilitado."
)

_USER_LEVELS = {
    "advogado": ResponseStyle.DETAILED,
    "estagiario": ResponseStyle.CONCISE,
    "cliente": ResponseStyle.PRACTICAL,
}


@lru_cache(maxsize=1)
def get_assistant() -> EnhancedVirtualAssistant:
    return EnhancedVirtualAssistant()


def _response_to_dict(response: Any, *, ai_enhanced: bool = False) -> dict[str, Any]:
    return {
        "query_id": response.query_id,
        "answer": response.answer,
        "confidence": float(response.confidence),
        "sources": response.sources,
        "related_concepts": response.related_concepts,
        "follow_up_questions": response.follow_up_questions,
        "response_time_ms": int(response.response_time * 1000),
        "disclaimer": DISCLAIMER,
        "metadata": {"ai_enhanced": ai_enhanced},
    }


def chat(
    message: str,
    user_level: str = "advogado",
    user_id: str = "api",
    enhance_with_gemini: bool = False,
) -> dict[str, Any]:
    style = _USER_LEVELS.get(user_level.lower(), ResponseStyle.CONCISE)
    assistant = get_assistant()

    if enhance_with_gemini:
        from ai_provider.gemini import generate_text, is_gemini_available
        from legal_core.prompts import load_prompt

        if not is_gemini_available():
            raise ValueError("GEMINI_API_KEY não configurada para o assistente.")

        local = assistant.process_query(message, user_id=user_id, style=style)
        system = (
            load_prompt("sistema-assistente-escritorio")
            .replace("{nivel_usuario}", user_level)
            .replace("{mensagem}", message)
        )
        user = f"""Mensagem do usuário:
{message}

Resposta preliminar (base local — refine se necessário):
{local.answer}

Produza resposta final em markdown, objetiva."""
        answer = generate_text(system, user, temperature=0.3, operation="assistant_chat")
        payload = _response_to_dict(local, ai_enhanced=True)
        payload["answer"] = answer
        return payload

    response = assistant.process_query(message, user_id=user_id, style=style)
    suggestions = assistant.suggest_related_queries(message)
    payload = _response_to_dict(response)
    payload["suggestions"] = suggestions
    return payload
