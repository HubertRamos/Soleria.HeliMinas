from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any


def _now() -> datetime:
    return datetime.now(UTC)


class Role(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class TurnState(str, Enum):
    """Estado terminal inequívoco de um turno."""

    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"
    ITERATION_LIMIT = "iteration_limit"


@dataclass(frozen=True)
class ToolCall:
    """Chamada de ferramenta normalizada. `id` é atribuído pelo loop."""

    id: str
    name: str
    arguments: dict[str, Any]


@dataclass(frozen=True)
class ToolResult:
    """Resultado de ferramenta. `ok=False` indica falha controlada."""

    call_id: str
    ok: bool
    content: str | None = None
    error_code: str | None = None
    error_message: str | None = None


@dataclass(frozen=True)
class Message:
    """Mensagem no contrato interno."""

    role: Role
    content: str | None = None
    tool_calls: tuple[ToolCall, ...] = ()
    tool_call_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=_now)


@dataclass(frozen=True)
class AgentError:
    """Erro normalizado do núcleo. Nunca carrega segredos."""

    code: str
    message: str
    recoverable: bool = False
    details: dict[str, Any] | None = None


@dataclass(frozen=True)
class TurnOutcome:
    """Resultado completo de um turno, para inspeção e testes."""

    state: TurnState
    final_message: Message | None
    error: AgentError | None
    iterations: int
