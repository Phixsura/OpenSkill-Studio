from app.services.app_marketplace_app_app_app_app_app_app_app_golden_signals import evaluate_golden_signals

def test_healthy():
    r = evaluate_golden_signals({"p99_ms": 100, "rps": 500, "error_rate_pct": 0.1,
                                  "cpu_pct": 40, "memory_pct": 50})
    assert r["status"] == "healthy"
    assert r["latency"]["ok"]

def test_degraded():
    r = evaluate_golden_signals({"p99_ms": 800, "rps": 500, "error_rate_pct": 5,
                                  "cpu_pct": 90, "memory_pct": 85,
                                  "latency_target_ms": 500, "error_target_pct": 1})
    assert r["status"] == "degraded"
    assert not r["latency"]["ok"]
    assert not r["errors"]["ok"]
    assert not r["saturation"]["ok"]
