from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Protocol


class Permission(str, Enum):
    READ = "read"
    WORKSPACE_WRITE = "workspace_write"
    EXECUTE = "execute"


@dataclass(frozen=True)
class Tool:
    name: str
    description: str
    parameters_schema: dict[str, Any]
    permission: Permission


@dataclass(frozen=True)
class ToolExecutionResult:
    ok: bool
    content: str | None = None
    error_code: str | None = None
    error_message: str | None = None


class ToolHandler(Protocol):
    """Implementação de uma ferramenta. Deve validar argumentos."""

    tool: Tool

    def execute(self, arguments: dict[str, Any]) -> ToolExecutionResult: ...
