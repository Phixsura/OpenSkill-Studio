"""Sandbox log parser tests."""

import pytest
from app.services.app_sandbox_log import parse_log_line, parse_logs, filter_logs

def test_parse_json_log():
    line = '{"level":"info","message":"started","timestamp":"2026-01-01T00:00:00Z"}'
    result = parse_log_line(line)
    assert result["level"] == "info"
    assert result["message"] == "started"

def test_parse_bracket_prefix():
    result = parse_log_line("[ERROR] connection failed")
    assert result["level"] == "error"
    assert result["message"] == "connection failed"

def test_parse_colon_prefix():
    result = parse_log_line("WARN: slow query detected")
    assert result["level"] == "warn"
    assert result["message"] == "slow query detected"

def test_parse_plain_text():
    result = parse_log_line("just a message")
    assert result["level"] == "info"
    assert result["message"] == "just a message"

def test_parse_empty():
    assert parse_log_line("") is None
    assert parse_log_line("   ") is None

def test_parse_ansi_strip():
    result = parse_log_line("\x1b[31mred text\x1b[0m")
    assert "\x1b" not in result["message"]
    assert "red text" in result["message"]

def test_parse_json_extra_fields():
    line = '{"level":"info","message":"req","duration_ms":150,"path":"/api"}'
    result = parse_log_line(line)
    assert result["extra"]["duration_ms"] == 150

def test_parse_logs_multiline():
    output = "[INFO] line 1\n[ERROR] line 2\n\n[DEBUG] line 3"
    logs = parse_logs(output)
    assert len(logs) == 3

def test_filter_by_level():
    logs = [
        {"level": "debug", "message": "d"},
        {"level": "info", "message": "i"},
        {"level": "warn", "message": "w"},
        {"level": "error", "message": "e"},
    ]
    assert len(filter_logs(logs, min_level="warn")) == 2
    assert len(filter_logs(logs, min_level="error")) == 1
    assert len(filter_logs(logs, min_level="debug")) == 4

def test_filter_default():
    logs = [{"level": "debug", "message": "d"}, {"level": "info", "message": "i"}]
    assert len(filter_logs(logs)) == 2
