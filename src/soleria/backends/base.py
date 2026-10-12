from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator, Sequence
from dataclasses import dataclass

from soleria.core.contracts import Message
from soleria.core.events import BackendEvent


@dataclass(frozen=True)
class BackendCapabilities:
    supports_tool_calls: bool
    supports_streaming: bool
    max_context: int
    model_id: str


class InferenceBackend(ABC):
    """Contrato do backend de inferência. Independente de provedor."""

    @property
    @abstractmethod
    def capabilities(self) -> BackendCapabilities: ...

    @abstractmethod
    async def generate(
        self,
        messages: Sequence[Message],
        tools: Sequence[dict],
        max_tokens: int,
    ) -> AsyncIterator[BackendEvent]:
        """Gera eventos normalizados. Deve respeitar cancelamento.

        Garantias:
        - `Done` ou `ErrorEvent` ou `Cancelled` é o último evento emitido.
        - O stream nunca é infinito.
        - Cancelamento do consumidor encerra o gerador.
        """
        raise NotImplementedError
