from app.services.app_sandbox_debug import format_debug_output

def test_success():
    d = format_debug_output(execution_id="e1", function_name="process", duration_ms=150, success=True,
        logs=[{"level": "info", "msg": "done"}], output={"result": "ok"}, error=None, env_vars=["API_KEY"])
    assert d["success"] is True
    assert d["log_count"] == 1
    assert d["env_vars_injected"] == 1

def test_failure():
    d = format_debug_output(execution_id="e2", function_name="sync", duration_ms=5000, success=False,
        logs=[], output=None, error="TimeoutError", env_vars=[])
    assert d["error"] == "TimeoutError"
    assert len(d["sections"]) == 4
