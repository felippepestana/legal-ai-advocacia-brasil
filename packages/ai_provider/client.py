from __future__ import annotations

import time
from typing import Any

from ai_provider.config import AIConfig
from ai_provider.context import get_ai_context


def generate_content(
    config: AIConfig,
    system_prompt: str,
    user_prompt: str,
    *,
    temperature: float = 0.3,
    max_output_tokens: int = 4096,
    operation: str | None = None,
) -> str:
    """Gera texto via google-genai (Vertex ou API key) com fallback para google-generativeai."""
    ctx = get_ai_context()
    op = operation or ctx.operation
    tenant_id = ctx.tenant_id
    started = time.monotonic()
    success = False
    output = ""
    error_msg: str | None = None

    try:
        try:
            output = _generate_with_genai(
                config, system_prompt, user_prompt, temperature, max_output_tokens
            )
        except ImportError:
            if config.backend != "api_key" or not config.api_key:
                raise RuntimeError(
                    "Instale google-genai para Vertex AI: pip install google-genai"
                ) from None
            output = _generate_with_legacy_sdk(
                config, system_prompt, user_prompt, temperature, max_output_tokens
            )
        success = True
        return output
    except Exception as exc:
        error_msg = str(exc)
        raise
    finally:
        latency_ms = int((time.monotonic() - started) * 1000)
        _write_audit(
            tenant_id=tenant_id,
            operation=op,
            config=config,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            latency_ms=latency_ms,
            success=success,
            error=error_msg,
            output_chars=len(output),
        )


def _write_audit(
    *,
    tenant_id: str,
    operation: str,
    config: AIConfig,
    system_prompt: str,
    user_prompt: str,
    latency_ms: int,
    success: bool,
    error: str | None,
    output_chars: int,
) -> None:
    try:
        from services.api.audit_store import log_ai_event

        log_ai_event(
            tenant_id=tenant_id,
            operation=operation,
            model=config.model,
            backend=config.backend,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            latency_ms=latency_ms,
            success=success,
            error=error,
            output_chars=output_chars,
        )
    except Exception:
        pass


def _generate_with_genai(
    config: AIConfig,
    system_prompt: str,
    user_prompt: str,
    temperature: float,
    max_output_tokens: int,
) -> str:
    from google import genai
    from google.genai import types

    if config.backend == "vertex":
        client = genai.Client(
            vertexai=True,
            project=config.project,
            location=config.location,
        )
    else:
        client = genai.Client(api_key=config.api_key)

    response = client.models.generate_content(
        model=config.model,
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
        ),
    )
    return _response_text(response)


def _generate_with_legacy_sdk(
    config: AIConfig,
    system_prompt: str,
    user_prompt: str,
    temperature: float,
    max_output_tokens: int,
) -> str:
    import google.generativeai as genai

    genai.configure(api_key=config.api_key)
    model = genai.GenerativeModel(config.model)
    response = model.generate_content(
        [system_prompt, user_prompt],
        generation_config={"temperature": temperature, "max_output_tokens": max_output_tokens},
    )
    return (response.text or "").strip()


def _response_text(response: Any) -> str:
    text = getattr(response, "text", None)
    if text:
        return text.strip()
    candidates = getattr(response, "candidates", None) or []
    for candidate in candidates:
        content = getattr(candidate, "content", None)
        if not content:
            continue
        parts = getattr(content, "parts", None) or []
        chunks = [getattr(p, "text", "") for p in parts if getattr(p, "text", None)]
        if chunks:
            return "\n".join(chunks).strip()
    return ""
