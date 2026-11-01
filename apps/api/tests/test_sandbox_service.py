"""Sandbox service — SandboxManager, SandboxResult, LogEntry."""

import pytest
from dataclasses import fields
from app.services.sandbox import SandboxManager, SandboxResult, LogEntry


def test_sandbox_result_fields():
    actual = {f.name for f in fields(SandboxResult)}
    assert {"success", "output", "logs", "duration_ms", "error"}.issubset(actual)

def test_sandbox_result_defaults():
    r = SandboxResult(success=True)
    assert r.success is True
    assert r.output is None
    assert r.logs == []
    assert r.duration_ms == 0
    assert r.error is None

def test_sandbox_result_failure():
    r = SandboxResult(success=False, error="timeout")
    assert r.success is False
    assert r.error == "timeout"

def test_log_entry_fields():
    actual = {f.name for f in fields(LogEntry)}
    assert {"level", "message", "timestamp"}.issubset(actual)

def test_sandbox_manager_instantiate():
    mgr = SandboxManager()
    assert mgr is not None

def test_sandbox_manager_has_execute():
    import inspect
    assert inspect.iscoroutinefunction(SandboxManager.execute)

def test_execute_params():
    import inspect
    params = inspect.signature(SandboxManager.execute).parameters
    assert "installation_id" in params
    assert "function_name" in params
    assert "payload" in params
    assert "timeout_seconds" in params
    assert "memory_mb" in params
