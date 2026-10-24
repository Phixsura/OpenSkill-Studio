from app.services.app_sandbox_performance_profiler import profile_executions, find_bottlenecks

EXECS = [{"function_name": "fast", "duration_ms": d} for d in [10, 20, 30, 40, 50]] + \
        [{"function_name": "slow", "duration_ms": d} for d in [500, 600, 700, 800, 1000]]

def test_profile():
    p = profile_executions(EXECS)
    assert "fast" in p and "slow" in p
    assert p["fast"]["avg_ms"] == 30.0

def test_bottlenecks():
    p = profile_executions(EXECS)
    b = find_bottlenecks(p, threshold_ms=500)
    assert len(b) == 1
    assert b[0]["function"] == "slow"

def test_empty():
    assert profile_executions([]) == {}
