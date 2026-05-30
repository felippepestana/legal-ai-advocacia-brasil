from __future__ import annotations

from contextvars import ContextVar, Token
from dataclasses import dataclass

_tenant_id: ContextVar[str] = ContextVar("ai_tenant_id", default="public")
_operation: ContextVar[str] = ContextVar("ai_operation", default="generate")


@dataclass(frozen=True)
class AIContext:
    tenant_id: str
    operation: str


def get_ai_context() -> AIContext:
    return AIContext(tenant_id=_tenant_id.get(), operation=_operation.get())


def bind_ai_context(*, tenant_id: str | None = None, operation: str | None = None) -> tuple[Token, Token]:
    t1 = _tenant_id.set(tenant_id or "public")
    t2 = _operation.set(operation or "generate")
    return t1, t2


def reset_ai_context(tokens: tuple[Token, Token]) -> None:
    _tenant_id.reset(tokens[0])
    _operation.reset(tokens[1])
