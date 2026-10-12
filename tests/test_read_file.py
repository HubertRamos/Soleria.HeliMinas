from __future__ import annotations

import os
from pathlib import Path

import pytest

from soleria.tools.read_file import ReadFileHandler


@pytest.fixture
def workspace(tmp_path: Path) -> Path:
    (tmp_path / "ok.txt").write_text("conteúdo", encoding="utf-8")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "inner.txt").write_text("interno", encoding="utf-8")
    return tmp_path


def handler(workspace: Path, **kwargs) -> ReadFileHandler:
    return ReadFileHandler(workspace, **kwargs)


def test_reads_file_inside_workspace(workspace: Path) -> None:
    result = handler(workspace).execute({"path": "ok.txt"})
    assert result.ok
    assert result.content == "conteúdo"


def test_reads_nested_file(workspace: Path) -> None:
    result = handler(workspace).execute({"path": "sub/inner.txt"})
    assert result.ok
    assert result.content == "interno"


def test_rejects_traversal(workspace: Path) -> None:
    result = handler(workspace).execute({"path": "../secret.txt"})
    assert not result.ok
    assert result.error_code == "path_rejected"


def test_rejects_absolute_path(workspace: Path) -> None:
    result = handler(workspace).execute({"path": "/etc/passwd"})
    assert not result.ok
    assert result.error_code == "path_rejected"


def test_rejects_external_symlink(workspace: Path, tmp_path_factory) -> None:
    outside = tmp_path_factory.mktemp("outside")
    secret = outside / "secret.txt"
    secret.write_text("não deveria ler", encoding="utf-8")
    link = workspace / "link.txt"
    os.symlink(secret, link)
    result = handler(workspace).execute({"path": "link.txt"})
    assert not result.ok
    assert result.error_code in {"path_rejected", "symlink_rejected"}


def test_rejects_large_file_by_truncation(workspace: Path) -> None:
    big = workspace / "big.txt"
    big.write_text("A" * 1024, encoding="utf-8")
    result = handler(workspace, max_bytes=64).execute({"path": "big.txt"})
    assert result.ok
    assert result.content is not None
    assert "truncado" in result.content


def test_rejects_invalid_arguments(workspace: Path) -> None:
    result = handler(workspace).execute({"path": ""})
    assert not result.ok
    assert result.error_code == "invalid_arguments"


def test_rejects_unknown_arguments(workspace: Path) -> None:
    result = handler(workspace).execute({"path": "ok.txt", "evil": True})
    assert not result.ok
    assert result.error_code == "invalid_arguments"


def test_missing_file_reports_not_found(workspace: Path) -> None:
    result = handler(workspace).execute({"path": "nao_existe.txt"})
    assert not result.ok
    assert result.error_code == "not_found"


def test_rejects_non_utf8(workspace: Path) -> None:
    bad = workspace / "bin.dat"
    bad.write_bytes(b"\xff\xfe\x00\x01")
    result = handler(workspace).execute({"path": "bin.dat"})
    assert not result.ok
    assert result.error_code == "decode_error"
