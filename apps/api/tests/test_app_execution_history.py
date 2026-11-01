from app.services.app_execution_history import record_execution, query_history

def test_record():
    e = record_execution(app_id="eh1", function_name="sync", success=True, duration_ms=100)
    assert e["success"] is True

def test_query():
    record_execution(app_id="eh2", function_name="process", success=True, duration_ms=50)
    record_execution(app_id="eh2", function_name="process", success=False, duration_ms=5000, error="timeout")
    all_entries = query_history("eh2")
    assert len(all_entries) >= 2

def test_query_by_function():
    record_execution(app_id="eh3", function_name="a", success=True, duration_ms=10)
    record_execution(app_id="eh3", function_name="b", success=True, duration_ms=20)
    assert len(query_history("eh3", function_name="a")) >= 1

def test_query_failures():
    record_execution(app_id="eh4", function_name="x", success=True, duration_ms=10)
    record_execution(app_id="eh4", function_name="x", success=False, duration_ms=100)
    failures = query_history("eh4", success=False)
    assert all(not e["success"] for e in failures)
