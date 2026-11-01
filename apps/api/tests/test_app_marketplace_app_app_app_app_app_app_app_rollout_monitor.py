from app.services.app_marketplace_app_app_app_app_app_app_app_rollout_monitor import monitor_rollout

def test_good():
    r = monitor_rollout({"current_pct": 25},
                         {"error_rate_pct": 0.5, "p99_ms": 100,
                          "baseline_error_rate": 0.3, "baseline_p99_ms": 90})
    assert r["health"] == "good"
    assert r["recommendation"] == "continue"

def test_bad_early():
    r = monitor_rollout({"current_pct": 10},
                         {"error_rate_pct": 10, "p99_ms": 500,
                          "baseline_error_rate": 0.5, "baseline_p99_ms": 100})
    assert r["health"] == "bad"
    assert r["recommendation"] == "pause"

def test_bad_late():
    r = monitor_rollout({"current_pct": 75},
                         {"error_rate_pct": 10, "p99_ms": 500,
                          "baseline_error_rate": 0.5, "baseline_p99_ms": 100})
    assert r["recommendation"] == "rollback"
