"""SandboxResult edge cases."""

from app.services.sandbox import SandboxResult


def test_success_with_output():
    r = SandboxResult(success=True, output={"result": [1, 2, 3]}, duration_ms=150)
    assert r.success
    assert r.output == {"result": [1, 2, 3]}
    assert r.duration_ms == 150

def test_failure_with_error():
    r = SandboxResult(success=False, error="TimeoutError: exceeded 30s", duration_ms=30000)
    assert not r.success
    assert "Timeout" in r.error

def test_with_logs():
    r = SandboxResult(success=True, logs=[
        {"level": "info", "message": "starting"},
        {"level": "warn", "message": "slow query"},
        {"level": "error", "message": "retry failed"},
    ])
    assert len(r.logs) == 3

def test_memory_peak():
    r = SandboxResult(success=True, memory_peak_mb=128.5)
    assert r.memory_peak_mb == 128.5

def test_default_values():
    r = SandboxResult(success=True)
    assert r.output is None
    assert r.logs == []
    assert r.duration_ms == 0
    assert r.memory_peak_mb == 0.0
    assert r.error is None

def test_large_output():
    big = {"data": list(range(1000))}
    r = SandboxResult(success=True, output=big)
    assert len(r.output["data"]) == 1000
