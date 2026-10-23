from app.services.app_marketplace_app_app_app_app_app_app_app_load_test import run_load_test, compare_runs

def test_run():
    r = run_load_test("/api/users", 100, 60, 85.0, 0.5)
    assert r["total_requests"] == 6000
    assert r["passed"]
    assert r["throughput_rps"] > 0

def test_compare():
    current = run_load_test("/api", 100, 60, 120.0, 1.5)
    baseline = run_load_test("/api", 100, 60, 80.0, 0.5)
    r = compare_runs(current, baseline)
    assert r["latency_change_ms"] == 40.0
    assert r["error_change_pct"] == 1.0
    assert r["regression"]
