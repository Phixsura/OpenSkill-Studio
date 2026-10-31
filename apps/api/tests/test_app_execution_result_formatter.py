from app.services.app_execution_result_formatter import format_execution_result, summarize_executions

def test_success_result():
    r = format_execution_result(success=True, output={"ok": True}, duration_ms=150)
    assert r["status"] == "completed"
    assert r["success"] is True

def test_failure_result():
    r = format_execution_result(success=False, error="timeout", duration_ms=30000)
    assert r["status"] == "failed"

def test_memory_rounded():
    r = format_execution_result(success=True, memory_mb=128.456)
    assert r["memory_mb"] == 128.5

def test_log_count():
    r = format_execution_result(success=True, logs=[{"msg": "a"}, {"msg": "b"}])
    assert r["log_count"] == 2

def test_summarize():
    results = [{"success": True, "duration_ms": 100}, {"success": True, "duration_ms": 200}, {"success": False, "duration_ms": 5000}]
    s = summarize_executions(results)
    assert s["total"] == 3
    assert s["success"] == 2
    assert s["success_rate"] == round(2/3*100, 1)

def test_summarize_empty():
    s = summarize_executions([])
    assert s["total"] == 0
    assert s["success_rate"] == 100.0
