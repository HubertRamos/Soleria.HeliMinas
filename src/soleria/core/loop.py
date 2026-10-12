from __future__ import annotations

import asyncio
import json
import uuid
from collections.abc import Sequence
from enum import Enum

from soleria.backends.base import InferenceBackend
from soleria.core.contracts import (
    AgentError,
    Message,
    Role,
    ToolCall,
    TurnOutcome,
    TurnState,
)
from soleria.core.events import (
    Cancelled,
    Done,
    ErrorEvent,
    TextDelta,
    ToolCallDelta,
)
from soleria.observability.logging import get_logger
from soleria.tools.executor import TrustedExecutor

logger = get_logger("soleria.core.loop")


DEFAULT_MAX_ITERATIONS = 8


class _BackendOutcome(Enum):
    """Resultado do consumo de um stream de backend.

    Distingue três desfechos que o loop precisa tratar de forma diferente:
    conclusão normal, falha do backend, e cancelamento observado.
    """

    OK = "ok"
    ERROR = "error"
    CANCELLED = "cancelled"


class AgentLoop:
    """Loop explícito do agente.

    Limites:
    - máximo de iterações por turno;
    - cada iteração é uma chamada ao backend;
    - cancelamento encerra imediatamente, sem retry.

    Fronteira de confiança:
    - o modelo nunca altera permissões, não ignora limites, não autoriza
      ferramentas. Apenas o TrustedExecutor decide o que executa.
    """

    def __init__(
        self,
        backend: InferenceBackend,
        executor: TrustedExecutor,
        *,
        system_prompt: str = "",
        max_iterations: int = DEFAULT_MAX_ITERATIONS,
        max_tokens_per_call: int = 512,
    ) -> None:
        self._backend = backend
        self._executor = executor
        self._system_prompt = system_prompt
        self._max_iterations = max_iterations
        self._max_tokens_per_call = max_tokens_per_call

    async def run_turn(
        self,
        history: Sequence[Message],
        user_input: str,
        *,
        cancel_event: asyncio.Event | None = None,
    ) -> TurnOutcome:
        turn_id = uuid.uuid4().hex[:12]
        messages: list[Message] = []
        if self._system_prompt:
            messages.append(Message(role=Role.SYSTEM, content=self._system_prompt))
        messages.extend(history)
        messages.append(Message(role=Role.USER, content=user_input))

        logger.info("turn_start", extra={"turn_id": turn_id})

        iterations = 0
        while iterations < self._max_iterations:
            if self._is_cancelled(cancel_event):
                logger.info(
                    "turn_cancelled",
                    extra={"turn_id": turn_id, "iterations": iterations},
                )
                return TurnOutcome(
                    state=TurnState.CANCELLED,
                    final_message=None,
                    error=None,
                    iterations=iterations,
                )

            iterations += 1
            try:
                outcome, assistant_message, tool_messages = await self._consume_backend(
                    messages,
                    turn_id,
                    cancel_event,
                )
            except asyncio.CancelledError:
                logger.info(
                    "turn_cancelled",
                    extra={"turn_id": turn_id, "iterations": iterations},
                )
                return TurnOutcome(
                    state=TurnState.CANCELLED,
                    final_message=None,
                    error=None,
                    iterations=iterations,
                )

            if outcome is _BackendOutcome.CANCELLED:
                logger.info(
                    "turn_cancelled",
                    extra={"turn_id": turn_id, "iterations": iterations},
                )
                return TurnOutcome(
                    state=TurnState.CANCELLED,
                    final_message=None,
                    error=None,
                    iterations=iterations,
                )

            if outcome is _BackendOutcome.ERROR or assistant_message is None:
                logger.info(
                    "turn_backend_error",
                    extra={"turn_id": turn_id, "iterations": iterations},
                )
                return TurnOutcome(
                    state=TurnState.FAILED,
                    final_message=None,
                    error=AgentError(code="backend_error", message="Falha no backend."),
                    iterations=iterations,
                )

            messages.append(assistant_message)

            if not tool_messages:
                logger.info(
                    "turn_end",
                    extra={"turn_id": turn_id, "iterations": iterations},
                )
                return TurnOutcome(
                    state=TurnState.COMPLETED,
                    final_message=assistant_message,
                    error=None,
                    iterations=iterations,
                )

            # Há resultados de ferramenta para devolver ao modelo.
            # Executa as válidas; as inválidas já vêm prontas como Message.
            for pending in tool_messages:
                if self._is_cancelled(cancel_event):
                    logger.info("turn_cancelled", extra={"turn_id": turn_id})
                    return TurnOutcome(
                        state=TurnState.CANCELLED,
                        final_message=None,
                        error=None,
                        iterations=iterations,
                    )
                messages.append(pending)

        logger.info("turn_iteration_limit", extra={"turn_id": turn_id})
        return TurnOutcome(
            state=TurnState.ITERATION_LIMIT,
            final_message=None,
            error=AgentError(
                code="iteration_limit",
                message=f"Limite de {self._max_iterations} iterações atingido.",
            ),
            iterations=iterations,
        )

    # -- Interno -----------------------------------------------------------

    @staticmethod
    def _is_cancelled(cancel_event: asyncio.Event | None) -> bool:
        return cancel_event is not None and cancel_event.is_set()

    async def _consume_backend(
        self,
        messages: list[Message],
        turn_id: str,
        cancel_event: asyncio.Event | None,
    ) -> tuple[_BackendOutcome, Message | None, list[Message]]:
        """Consome um stream do backend.

        Retorna:
        - outcome: OK, ERROR ou CANCELLED;
        - assistant_message: apenas se outcome for OK;
        - tool_messages: apenas se outcome for OK. Inclui tanto resultados
          de ferramentas válidas executadas pelo TrustedExecutor quanto
          mensagens sintéticas de erro para tool calls malformadas, para
          que o modelo veja o que foi rejeitado.
        """
        tools = self._executor.known_tools()
        text_parts: list[str] = []
        pending: dict[int, dict] = {}
        done = False

        try:
            async for event in self._backend.generate(
                messages,
                tools,
                self._max_tokens_per_call,
            ):
                if self._is_cancelled(cancel_event):
                    logger.info("backend_cancelled", extra={"turn_id": turn_id})
                    return _BackendOutcome.CANCELLED, None, []

                if isinstance(event, TextDelta):
                    text_parts.append(event.content)
                elif isinstance(event, ToolCallDelta):
                    slot = pending.setdefault(
                        event.index,
                        {"id": None, "name": None, "args": ""},
                    )
                    if event.id:
                        slot["id"] = event.id
                    if event.name:
                        slot["name"] = event.name
                    slot["args"] += event.arguments_delta
                elif isinstance(event, Done):
                    done = True
                elif isinstance(event, Cancelled):
                    logger.info("backend_cancelled", extra={"turn_id": turn_id})
                    return _BackendOutcome.CANCELLED, None, []
                elif isinstance(event, ErrorEvent):
                    logger.info(
                        "backend_error",
                        extra={"turn_id": turn_id, "code": event.code},
                    )
                    return _BackendOutcome.ERROR, None, []
        except asyncio.CancelledError:
            raise

        if not done:
            logger.info("backend_incomplete", extra={"turn_id": turn_id})
            return _BackendOutcome.ERROR, None, []

        final_text = "".join(text_parts)
        assistant_message = Message(
            role=Role.ASSISTANT,
            content=final_text or None,
            tool_calls=tuple(),
        )

        tool_messages: list[Message] = []

        for index in sorted(pending):
            slot = pending[index]
            call_id = slot["id"] or f"invalid-{index}"

            # Sem nome ou sem id: a chamada não pode sequer ser identificada.
            if not slot["name"] or slot["id"] is None:
                logger.info(
                    "tool_call_malformed",
                    extra={"turn_id": turn_id, "index": index},
                )
                tool_messages.append(
                    Message(
                        role=Role.TOOL,
                        content=None,
                        tool_call_id=call_id,
                        metadata={"ok": False, "error_code": "malformed_tool_call"},
                    )
                )
                continue

            # Argumentos precisam ser JSON decodificável e objeto.
            try:
                parsed = json.loads(slot["args"] or "{}")
            except json.JSONDecodeError:
                logger.info(
                    "tool_call_arguments_invalid_json",
                    extra={"turn_id": turn_id, "name": slot["name"]},
                )
                tool_messages.append(
                    Message(
                        role=Role.TOOL,
                        content=None,
                        tool_call_id=call_id,
                        metadata={"ok": False, "error_code": "invalid_arguments_json"},
                    )
                )
                continue

            if not isinstance(parsed, dict):
                logger.info(
                    "tool_call_arguments_not_object",
                    extra={"turn_id": turn_id, "name": slot["name"]},
                )
                tool_messages.append(
                    Message(
                        role=Role.TOOL,
                        content=None,
                        tool_call_id=call_id,
                        metadata={"ok": False, "error_code": "arguments_not_object"},
                    )
                )
                continue

            call = ToolCall(id=call_id, name=slot["name"], arguments=parsed)

            # A partir daqui, a decisão de executar é do TrustedExecutor.
            result = self._executor.execute(call)
            tool_messages.append(
                Message(
                    role=Role.TOOL,
                    content=result.content if result.ok else None,
                    tool_call_id=result.call_id,
                    metadata={
                        "ok": result.ok,
                        "error_code": result.error_code,
                        "error_message": result.error_message,
                    },
                )
            )

        return _BackendOutcome.OK, assistant_message, tool_messages
