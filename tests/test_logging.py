from __future__ import annotations

import json
import logging

from soleria.observability.logging import JsonFormatter


def _record(**extra) -> logging.LogRecord:
    record = logging.LogRecord(
        name="soleria.test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="evento",
        args=(),
        exc_info=None,
    )
    for k, v in extra.items():
        setattr(record, k, v)
    return record


def test_log_is_json() -> None:
    line = JsonFormatter().format(_record(tool="read_file", turn_id="abc"))
    payload = json.loads(line)
    assert payload["event"] == "evento"
    assert payload["tool"] == "read_file"
    assert payload["turn_id"] == "abc"


def test_sensitive_fields_redacted() -> None:
    line = JsonFormatter().format(_record(content="segredo", file_content="x"))
    payload = json.loads(line)
    assert payload["content"] == "[redacted]"
    assert payload["file_content"] == "[redacted]"
