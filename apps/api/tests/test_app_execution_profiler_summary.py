from app.services.app_execution_profiler_summary import build_profiler_summary

EXECS = [
    {"function_name": "fast", "duration_ms": 10},
    {"function_name": "fast", "duration_ms": 20},
    {"function_name": "slow", "duration_ms": 500},
    {"function_name": "slow", "duration_ms": 600},
]

def test_summary():
    s = build_profiler_summary(EXECS)
    assert s["total"] == 4
    assert s["slowest_function"] == "slow"
    assert s["fastest_function"] == "fast"

def test_empty():
    s = build_profiler_summary([])
    assert s["total"] == 0
    assert s["slowest_function"] is None

def test_function_count():
    s = build_profiler_summary(EXECS)
    assert s["function_count"] == 2
