"""Tests for sandbox service internals."""

from app.services.sandbox import (
    DEFAULT_MEMORY_MB,
    DEFAULT_TIMEOUT_SECONDS,
    MAX_MEMORY_MB,
    MAX_OUTPUT_BYTES,
    MAX_TIMEOUT_SECONDS,
    LogEntry,
    SandboxManager,
    SandboxResult,
)


def test_sandbox_result_success():
    r = SandboxResult(success=True, output={"key": "val"}, duration_ms=150)
    assert r.success is True
    assert r.output == {"key": "val"}
    assert r.duration_ms == 150


def test_sandbox_result_failure():
    r = SandboxResult(success=False, error="timeout", duration_ms=30000)
    assert r.success is False
    assert r.error == "timeout"


def test_sandbox_result_with_logs():
    r = SandboxResult(success=True, logs=[{"level": "info", "message": "test"}])
    assert len(r.logs) == 1


def test_sandbox_result_defaults():
    r = SandboxResult(success=True)
    assert r.output is None
    assert r.logs == []
    assert r.duration_ms == 0
    assert r.memory_peak_mb == 0.0
    assert r.error is None


def test_log_entry():
    entry = LogEntry(level="info", message="test msg", timestamp="2026-01-01T00:00:00Z")
    assert entry.level == "info"
    assert entry.message == "test msg"


def test_sandbox_constants():
    assert DEFAULT_TIMEOUT_SECONDS == 30
    assert MAX_TIMEOUT_SECONDS == 300
    assert DEFAULT_MEMORY_MB == 128
    assert MAX_MEMORY_MB == 512
    assert MAX_OUTPUT_BYTES == 1_000_000


def test_sandbox_manager_instantiation():
    mgr = SandboxManager()
    assert mgr is not None
    assert hasattr(mgr, "execute")
