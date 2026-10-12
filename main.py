"""Ponto de entrada mínimo do protótipo Soleria.

Este arquivo existe para provar o ciclo do agente com um backend falso.
Nenhum modelo real é carregado aqui.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from soleria.backends.fake import FakeBackend, script_text
from soleria.core.loop import AgentLoop
from soleria.identity.heliminas import HELIMINAS_SYSTEM_PROMPT
from soleria.observability.logging import configure_logging
from soleria.tools.executor import TrustedExecutor
from soleria.tools.read_file import ReadFileHandler


async def _amain() -> int:
    configure_logging()
    workspace = Path.cwd()

    backend = FakeBackend(scripts=[script_text("Oi. Backend falso funcionando.")])
    executor = TrustedExecutor({"read_file": ReadFileHandler(workspace)})
    loop = AgentLoop(
        backend=backend,
        executor=executor,
        system_prompt=HELIMINAS_SYSTEM_PROMPT,
    )

    outcome = await loop.run_turn(history=[], user_input="Olá, Soleria.")
    print(f"[estado] {outcome.state.value}")
    if outcome.final_message and outcome.final_message.content:
        print(f"[resposta] {outcome.final_message.content}")
    return 0


def main() -> int:
    return asyncio.run(_amain())


if __name__ == "__main__":
    sys.exit(main())
