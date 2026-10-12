from __future__ import annotations

from dataclasses import dataclass
from typing import Union


@dataclass(frozen=True)
class TextDelta:
    content: str


@dataclass(frozen=True)
class ToolCallDelta:
    """Fragmento de chamada de ferramenta.

    `index` identifica a chamada em construção. `id` e `name` podem chegar
    apenas no primeiro fragmento. `arguments_delta` é texto JSON fragmentado.
    """

    index: int
    id: str | None
    name: str | None
    arguments_delta: str


@dataclass(frozen=True)
class Done:
    """Conclusão normal do stream. `finish_reason` é informativo."""

    finish_reason: str = "stop"


@dataclass(frozen=True)
class ErrorEvent:
    """Falha do backend. Encerra o stream imediatamente."""

    code: str
    message: str
    recoverable: bool = False


@dataclass(frozen=True)
class Cancelled:
    """Cancelamento observado do lado do backend."""

    reason: str = "user_cancelled"


BackendEvent = Union[TextDelta, ToolCallDelta, Done, ErrorEvent, Cancelled]
