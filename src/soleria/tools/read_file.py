from __future__ import annotations

import errno
import os
from pathlib import Path
from typing import Any

from soleria.tools.base import (
    Permission,
    Tool,
    ToolExecutionResult,
)

MAX_BYTES_DEFAULT = 256 * 1024  # 256 KiB


READ_FILE_TOOL = Tool(
    name="read_file",
    description=(
        "Lê o conteúdo de um arquivo de texto dentro do workspace autorizado. "
        "Não segue links simbólicos que escapem do workspace."
    ),
    parameters_schema={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Caminho relativo ao workspace.",
            },
            "max_bytes": {
                "type": "integer",
                "description": "Limite de bytes a ler.",
                "minimum": 1,
                "maximum": MAX_BYTES_DEFAULT,
            },
        },
        "required": ["path"],
        "additionalProperties": False,
    },
    permission=Permission.READ,
)


class ReadFileHandler:
    tool = READ_FILE_TOOL

    def __init__(self, workspace: Path, *, max_bytes: int = MAX_BYTES_DEFAULT) -> None:
        resolved = workspace.resolve(strict=True)
        if not resolved.is_dir():
            raise ValueError(f"Workspace inválido: {resolved}")
        self._workspace = resolved
        self._max_bytes = max_bytes

    # -- API pública -------------------------------------------------------

    def execute(self, arguments: dict[str, Any]) -> ToolExecutionResult:
        try:
            path_arg, max_bytes = self._parse_arguments(arguments)
        except ValueError as exc:
            return ToolExecutionResult(
                ok=False,
                error_code="invalid_arguments",
                error_message=str(exc),
            )

        try:
            target = self._safe_target(path_arg)
        except ValueError as exc:
            return ToolExecutionResult(
                ok=False,
                error_code="path_rejected",
                error_message=str(exc),
            )

        return self._read(target, max_bytes)

    # -- Interno -----------------------------------------------------------

    def _parse_arguments(self, arguments: dict[str, Any]) -> tuple[str, int]:
        if not isinstance(arguments, dict):
            raise ValueError("Argumentos devem ser um objeto.")
        if set(arguments.keys()) - {"path", "max_bytes"}:
            raise ValueError("Argumentos desconhecidos.")
        path = arguments.get("path")
        if not isinstance(path, str) or not path:
            raise ValueError("'path' é obrigatório e deve ser string não vazia.")
        max_bytes = arguments.get("max_bytes", self._max_bytes)
        if not isinstance(max_bytes, int) or isinstance(max_bytes, bool):
            raise ValueError("'max_bytes' deve ser inteiro.")
        if max_bytes < 1 or max_bytes > self._max_bytes:
            raise ValueError(
                f"'max_bytes' fora do intervalo permitido (1..{self._max_bytes})."
            )
        return path, max_bytes

    def _safe_target(self, path_arg: str) -> Path:
        # Caminhos absolutos são rejeitados por política.
        if os.path.isabs(path_arg):
            raise ValueError("Caminhos absolutos não são permitidos.")

        # Normalização textual primeiro (defesa em profundidade).
        normalized = os.path.normpath(path_arg)
        if normalized.startswith("..") or os.path.isabs(normalized):
            raise ValueError("Caminho fora do workspace.")

        candidate = self._workspace / normalized
        # resolve(strict=False) segue symlinks; verificamos se o resultado
        # permanece dentro do workspace ANTES de abrir.
        try:
            resolved = candidate.resolve(strict=False)
        except OSError as exc:
            raise ValueError(f"Caminho inválido: {exc}") from exc

        try:
            resolved.relative_to(self._workspace)
        except ValueError as exc:
            raise ValueError("Caminho escapa do workspace.") from exc

        return resolved

    def _read(self, target: Path, max_bytes: int) -> ToolExecutionResult:
        # O_NOFOLLOW no componente final impede que o último segmento seja um
        # symlink apontando para fora — defesa complementar ao resolve().
        flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0)
        try:
            fd = os.open(target, flags)
        except FileNotFoundError:
            return ToolExecutionResult(
                ok=False,
                error_code="not_found",
                error_message="Arquivo não encontrado.",
            )
        except IsADirectoryError:
            return ToolExecutionResult(
                ok=False,
                error_code="is_directory",
                error_message="O caminho é um diretório.",
            )
        except OSError as exc:
            if exc.errno == errno.ELOOP:
                return ToolExecutionResult(
                    ok=False,
                    error_code="symlink_rejected",
                    error_message="Link simbólico não permitido no destino final.",
                )
            return ToolExecutionResult(
                ok=False,
                error_code="io_error",
                error_message="Falha ao abrir o arquivo.",
            )

        try:
            with os.fdopen(fd, "rb") as handle:
                data = handle.read(max_bytes + 1)
            if len(data) > max_bytes:
                data = data[:max_bytes]
                truncated = True
            else:
                truncated = False
        except OSError:
            return ToolExecutionResult(
                ok=False, error_code="io_error", error_message="Falha ao ler o arquivo."
            )

        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            return ToolExecutionResult(
                ok=False,
                error_code="decode_error",
                error_message="Arquivo não é texto UTF-8.",
            )

        if truncated:
            text += f"\n[... truncado em {max_bytes} bytes ...]"

        return ToolExecutionResult(ok=True, content=text)
