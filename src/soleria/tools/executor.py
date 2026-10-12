from __future__ import annotations

import logging
from collections.abc import Mapping

from soleria.core.contracts import ToolCall, ToolResult
from soleria.tools.base import Permission, ToolExecutionResult, ToolHandler

logger = logging.getLogger("soleria.tools.executor")


class TrustedExecutor:
    """Executor que aplica permissão antes de delegar ao handler.

    Decisões de permissão NÃO são tomadas pelo modelo. O executor confia
    apenas em seu próprio estado e nos handlers registrados.
    """

    def __init__(self, handlers: Mapping[str, ToolHandler]) -> None:
        self._handlers = dict(handlers)

    def known_tools(self) -> list[dict]:
        return [
            {
                "name": h.tool.name,
                "description": h.tool.description,
                "parameters": h.tool.parameters_schema,
            }
            for h in self._handlers.values()
        ]

    def execute(self, call: ToolCall) -> ToolResult:
        handler = self._handlers.get(call.name)
        if handler is None:
            logger.info(
                "tool_unknown",
                extra={"tool": call.name, "call_id": call.id},
            )
            return ToolResult(
                call_id=call.id,
                ok=False,
                error_code="unknown_tool",
                error_message=f"Ferramenta '{call.name}' não registrada.",
            )

        # Permissão é verificada contra o próprio handler, não contra o modelo.
        # Nesta fase, todas as ferramentas registradas já estão pré-autorizadas
        # pelo código do executor. A verificação explícita fica registrada.
        permission = handler.tool.permission
        if permission not in (
            Permission.READ,
            Permission.WORKSPACE_WRITE,
            Permission.EXECUTE,
        ):
            logger.error(
                "tool_permission_invalid",
                extra={"tool": call.name, "permission": str(permission)},
            )
            return ToolResult(
                call_id=call.id,
                ok=False,
                error_code="permission_misconfigured",
                error_message="Permissão da ferramenta inválida.",
            )

        try:
            result: ToolExecutionResult = handler.execute(call.arguments)
        except Exception:
            # Nunca vazar traceback bruto para o modelo.
            logger.exception(
                "tool_crashed",
                extra={"tool": call.name, "call_id": call.id},
            )
            return ToolResult(
                call_id=call.id,
                ok=False,
                error_code="tool_crashed",
                error_message="Erro interno ao executar a ferramenta.",
            )

        logger.info(
            "tool_executed",
            extra={
                "tool": call.name,
                "call_id": call.id,
                "ok": result.ok,
                "permission": permission.value,
            },
        )

        if result.ok:
            return ToolResult(call_id=call.id, ok=True, content=result.content or "")
        return ToolResult(
            call_id=call.id,
            ok=False,
            error_code=result.error_code or "tool_error",
            error_message=result.error_message or "Erro na ferramenta.",
        )
