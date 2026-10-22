"""Parametrized SandboxResult tests."""

import pytest
from app.services.sandbox import SandboxResult

RESULTS = [
    (True, {"ok": True}, None, 100, "success with output"),
    (True, None, None, 0, "success no output"),
    (False, None, "timeout", 30000, "timeout failure"),
    (False, None, "crash", 500, "crash failure"),
    (True, {"data": [1, 2, 3]}, None, 50, "success with list output"),
]

@pytest.mark.parametrize("success,output,error,duration,desc", RESULTS, ids=lambda x: x if isinstance(x, str) else "r")
def test_sandbox_result(success, output, error, duration, desc):
    r = SandboxResult(success=success, output=output, error=error, duration_ms=duration)
    assert r.success == success
    assert r.output == output
    assert r.error == error
    assert r.duration_ms == duration

@pytest.mark.parametrize("success,output,error,duration,desc", RESULTS, ids=lambda x: x if isinstance(x, str) else "r")
def test_sandbox_result_defaults(success, output, error, duration, desc):
    r = SandboxResult(success=success)
    assert r.logs == []
    assert r.memory_peak_mb == 0.0
