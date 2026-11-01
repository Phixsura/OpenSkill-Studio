from app.services.app_execution_log_aggregator import aggregate_by_function, find_slow_functions

EXECS = [
    {"function_name": "sync", "duration_ms": 100, "success": True},
    {"function_name": "sync", "duration_ms": 200, "success": True},
    {"function_name": "sync", "duration_ms": 5000, "success": False, "error": "timeout"},
    {"function_name": "process", "duration_ms": 50, "success": True},
]

def test_aggregate():
    agg = aggregate_by_function(EXECS)
    sync = next(a for a in agg if a["function"] == "sync")
    assert sync["count"] == 3
    assert sync["unique_errors"] == 1

def test_aggregate_sorted():
    agg = aggregate_by_function(EXECS)
    assert agg[0]["function"] == "sync"  # most executions first

def test_slow():
    slow = find_slow_functions(EXECS, threshold_ms=1000)
    assert len(slow) == 1
    assert slow[0]["duration_ms"] == 5000

def test_empty():
    assert aggregate_by_function([]) == []
    assert find_slow_functions([]) == []
