from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Sequence

from soleria.backends.base import BackendCapabilities, InferenceBackend
from soleria.core.contracts import Message
from soleria.core.events import (
    BackendEvent,
    Cancelled,
    Done,
    ErrorEvent,
    TextDelta,
    ToolCallDelta,
)


class FakeBackend(InferenceBackend):
    """Backend determinístico. Cada turno consome o próximo roteiro.

    O roteiro é uma lista de eventos. Se a lista se esgotar, `Done` é emitido.
    Para simular cancelamento, use `await backend.cancel()` ou inclua `Cancelled`.
    """

    def __init__(
        self,
        scripts: list[list[BackendEvent]],
        *,
        model_id: str = "fake",
    ) -> None:
        self._scripts = [list(s) for s in scripts]
        self._index = 0
        self._cancel_requested = False
        self._capabilities = BackendCapabilities(
            supports_tool_calls=True,
            supports_streaming=True,
            max_context=8192,
            model_id=model_id,
        )

    @property
    def capabilities(self) -> BackendCapabilities:
        return self._capabilities

    async def cancel(self) -> None:
        self._cancel_requested = True

    async def generate(
        self,
        messages: Sequence[Message],
        tools: Sequence[dict],
        max_tokens: int,
    ) -> AsyncIterator[BackendEvent]:
        self._cancel_requested = False
        script = self._scripts[self._index] if self._index < len(self._scripts) else []
        self._index += 1

        for event in script:
            if self._cancel_requested:
                yield Cancelled(reason="user_cancelled")
                return
            yield event
            await asyncio.sleep(0)  # permite cancelamento cooperativo

        if self._cancel_requested:
            yield Cancelled(reason="user_cancelled")
            return
        yield Done(finish_reason="stop")


def script_text(text: str) -> list[BackendEvent]:
    """Helper: roteiro que emite texto e conclui."""
    return [TextDelta(content=text), Done()]


def script_tool_call(
    *, call_id: str, name: str, arguments_json: str, leading_text: str = ""
) -> list[BackendEvent]:
    """Helper: roteiro que emite uma chamada de ferramenta."""
    events: list[BackendEvent] = []
    if leading_text:
        events.append(TextDelta(content=leading_text))
    events.append(
        ToolCallDelta(index=0, id=call_id, name=name, arguments_delta=arguments_json)
    )
    events.append(Done(finish_reason="tool_calls"))
    return events


def script_error(code: str, message: str) -> list[BackendEvent]:
    return [ErrorEvent(code=code, message=message, recoverable=False)]
