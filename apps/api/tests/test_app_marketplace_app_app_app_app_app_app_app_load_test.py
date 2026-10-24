from app.services.app_marketplace_app_app_app_app_app_app_app_load_test import analyze_load_test, compare_runs

def test_analyze():
    r = analyze_load_test({"total_requests": 10000, "failed_requests": 5,
                           "duration_seconds": 60, "p50_ms": 20, "p95_ms": 80, "p99_ms": 150})
    assert r["rps"] == 166.7
    assert r["error_rate_pct"] == 0.05
    assert r["passed"]

def test_compare():
    baseline = {"rps": 100, "p99_ms": 200, "error_rate_pct": 0.1}
    current = {"rps": 120, "p99_ms": 180, "error_rate_pct": 0.05}
    r = compare_runs(baseline, current)
    assert r["rps_change_pct"] == 20.0
    assert not r["regression"]
