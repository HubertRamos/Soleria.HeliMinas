from __future__ import annotations

import asyncio
from pathlib import Path

import pytest

from soleria.backends.fake import (
    FakeBackend,
    script_error,
    script_text,
    script_tool_call,
)
from soleria.core.contracts import TurnState
from soleria.core.events import (
    Done,
    TextDelta,
)
from soleria.core.loop import AgentLoop
from soleria.tools.executor import TrustedExecutor
from soleria.tools.read_file import ReadFileHandler


@pytest.fixture
def workspace(tmp_path: Path) -> Path:
    (tmp_path / "hello.txt").write_text("conteúdo de teste", encoding="utf-8")
    return tmp_path


def make_loop(workspace: Path, scripts) -> AgentLoop:
    backend = FakeBackend(scripts=scripts)
    executor = TrustedExecutor({"read_file": ReadFileHandler(workspace)})
    return AgentLoop(backend=backend, executor=executor, system_prompt="SYS")


@pytest.mark.asyncio
async def test_final_text_ends_turn(workspace: Path) -> None:
    loop = make_loop(workspace, [script_text("Olá!")])
    outcome = await loop.run_turn([], "oi")
    assert outcome.state is TurnState.COMPLETED
    assert outcome.final_message is not None
    assert outcome.final_message.content == "Olá!"
    assert outcome.iterations == 1


@pytest.mark.asyncio
async def test_valid_tool_call_is_executed(workspace: Path) -> None:
    scripts = [
        script_tool_call(
            call_id="c1",
            name="read_file",
            arguments_json='{"path": "hello.txt"}',
        ),
        script_text("Li o arquivo."),
    ]
    loop = make_loop(workspace, scripts)
    outcome = await loop.run_turn([], "leia hello.txt")
    assert outcome.state is TurnState.COMPLETED
    assert outcome.iterations == 2
    assert outcome.final_message is not None
    assert outcome.final_message.content == "Li o arquivo."


@pytest.mark.asyncio
async def test_invalid_tool_call_not_executed(workspace: Path) -> None:
    scripts = [
        script_tool_call(
            call_id="c1",
            name="read_file",
            arguments_json="{not valid json",
        ),
        script_text("Não consegui ler."),
    ]
    loop = make_loop(workspace, scripts)
    outcome = await loop.run_turn([], "leia algo")
    assert outcome.state is TurnState.COMPLETED
    # Primeira iteração não executa a ferramenta; segunda conclui.
    assert outcome.iterations == 2


@pytest.mark.asyncio
async def test_unknown_tool_not_executed(workspace: Path) -> None:
    scripts = [
        script_tool_call(call_id="c1", name="rm_rf", arguments_json="{}"),
        script_text("Não posso."),
    ]
    loop = make_loop(workspace, scripts)
    outcome = await loop.run_turn([], "apague tudo")
    assert outcome.state is TurnState.COMPLETED
    assert outcome.iterations == 2


@pytest.mark.asyncio
async def test_backend_error_fails_turn(workspace: Path) -> None:
    loop = make_loop(workspace, [script_error("boom", "falhou")])
    outcome = await loop.run_turn([], "oi")
    assert outcome.state is TurnState.FAILED
    assert outcome.error is not None
    assert outcome.error.code == "backend_error"


@pytest.mark.asyncio
async def test_iteration_limit(workspace: Path) -> None:
    # Roteiro sempre pede ferramenta — loop deve parar por limite.
    scripts = [
        script_tool_call(
            call_id=f"c{i}",
            name="read_file",
            arguments_json='{"path": "hello.txt"}',
        )
        for i in range(20)
    ]
    backend = FakeBackend(scripts=scripts)
    executor = TrustedExecutor({"read_file": ReadFileHandler(workspace)})
    loop = AgentLoop(
        backend=backend,
        executor=executor,
        system_prompt="SYS",
        max_iterations=3,
    )
    outcome = await loop.run_turn([], "loop")
    assert outcome.state is TurnState.ITERATION_LIMIT
    assert outcome.iterations == 3


@pytest.mark.asyncio
async def test_cancellation_before_turn(workspace: Path) -> None:
    loop = make_loop(workspace, [script_text("nunca")])
    cancel = asyncio.Event()
    cancel.set()
    outcome = await loop.run_turn([], "oi", cancel_event=cancel)
    assert outcome.state is TurnState.CANCELLED
    assert outcome.iterations == 0


@pytest.mark.asyncio
async def test_cancellation_during_backend(workspace: Path) -> None:
    class SlowBackend(FakeBackend):
        async def generate(self, messages, tools, max_tokens):
            yield TextDelta("começando")
            await asyncio.sleep(0.05)
            yield Done()

    backend = SlowBackend(scripts=[])
    executor = TrustedExecutor({"read_file": ReadFileHandler(workspace)})
    loop = AgentLoop(backend=backend, executor=executor, system_prompt="SYS")
    cancel = asyncio.Event()

    async def trigger():
        await asyncio.sleep(0.01)
        cancel.set()

    asyncio.create_task(trigger())
    outcome = await loop.run_turn([], "oi", cancel_event=cancel)
    assert outcome.state is TurnState.CANCELLED


@pytest.fixture
def workspace(tmp_path: Path) -> Path:
    (tmp_path / "hello.txt").write_text("conteúdo de teste", encoding="utf-8")
    return tmp_path


def make_loop(workspace: Path, scripts) -> AgentLoop:
    backend = FakeBackend(scripts=scripts)
    executor = TrustedExecutor({"read_file": ReadFileHandler(workspace)})
    return AgentLoop(backend=backend, executor=executor, system_prompt="SYS")


@pytest.mark.asyncio
async def test_final_text_ends_turn(workspace: Path) -> None:
    loop = make_loop(workspace, [script_text("Olá!")])
    outcome = await loop.run_turn([], "oi")
    assert outcome.state is TurnState.COMPLETED
    assert outcome.final_message is not None
    assert outcome.final_message.content == "Olá!"
    assert outcome.iterations == 1


@pytest.mark.asyncio
async def test_valid_tool_call_is_executed(workspace: Path) -> None:
    scripts = [
        script_tool_call(
            call_id="c1",
            name="read_file",
            arguments_json='{"path": "hello.txt"}',
        ),
        script_text("Li o arquivo."),
    ]
    loop = make_loop(workspace, scripts)
    outcome = await loop.run_turn([], "leia hello.txt")
    assert outcome.state is TurnState.COMPLETED
    assert outcome.iterations == 2
    assert outcome.final_message is not None
    assert outcome.final_message.content == "Li o arquivo."


@pytest.mark.asyncio
async def test_invalid_tool_call_not_executed(workspace: Path) -> None:
    scripts = [
        script_tool_call(
            call_id="c1",
            name="read_file",
            arguments_json="{not valid json",
        ),
        script_text("Não consegui ler."),
    ]
    loop = make_loop(workspace, scripts)
    outcome = await loop.run_turn([], "leia algo")
    assert outcome.state is TurnState.COMPLETED
    # Primeira iteração não executa a ferramenta; segunda conclui.
    assert outcome.iterations == 2


@pytest.mark.asyncio
async def test_unknown_tool_not_executed(workspace: Path) -> None:
    scripts = [
        script_tool_call(call_id="c1", name="rm_rf", arguments_json="{}"),
        script_text("Não posso."),
    ]
    loop = make_loop(workspace, scripts)
    outcome = await loop.run_turn([], "apague tudo")
    assert outcome.state is TurnState.COMPLETED
    assert outcome.iterations == 2


@pytest.mark.asyncio
async def test_backend_error_fails_turn(workspace: Path) -> None:
    loop = make_loop(workspace, [script_error("boom", "falhou")])
    outcome = await loop.run_turn([], "oi")
    assert outcome.state is TurnState.FAILED
    assert outcome.error is not None
    assert outcome.error.code == "backend_error"


@pytest.mark.asyncio
async def test_iteration_limit(workspace: Path) -> None:
    # Roteiro sempre pede ferramenta — loop deve parar por limite.
    scripts = [
        script_tool_call(
            call_id=f"c{i}",
            name="read_file",
            arguments_json='{"path": "hello.txt"}',
        )
        for i in range(20)
    ]
    backend = FakeBackend(scripts=scripts)
    executor = TrustedExecutor({"read_file": ReadFileHandler(workspace)})
    loop = AgentLoop(
        backend=backend,
        executor=executor,
        system_prompt="SYS",
        max_iterations=3,
    )
    outcome = await loop.run_turn([], "loop")
    assert outcome.state is TurnState.ITERATION_LIMIT
    assert outcome.iterations == 3


@pytest.mark.asyncio
async def test_cancellation_before_turn(workspace: Path) -> None:
    loop = make_loop(workspace, [script_text("nunca")])
    cancel = asyncio.Event()
    cancel.set()
    outcome = await loop.run_turn([], "oi", cancel_event=cancel)
    assert outcome.state is TurnState.CANCELLED
    assert outcome.iterations == 0


@pytest.mark.asyncio
async def test_cancellation_during_backend(workspace: Path) -> None:
    class SlowBackend(FakeBackend):
        async def generate(self, messages, tools, max_tokens):
            yield TextDelta("começando")
            await asyncio.sleep(0.05)
            yield Done()

    backend = SlowBackend(scripts=[])
    executor = TrustedExecutor({"read_file": ReadFileHandler(workspace)})
    loop = AgentLoop(backend=backend, executor=executor, system_prompt="SYS")
    cancel = asyncio.Event()

    async def trigger():
        await asyncio.sleep(0.01)
        cancel.set()

    asyncio.create_task(trigger())
    outcome = await loop.run_turn([], "oi", cancel_event=cancel)
    assert outcome.state is TurnState.CANCELLED
