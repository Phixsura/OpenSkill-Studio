from app.services.app_marketplace_app_app_app_app_app_app_app_canary_analyze import analyze_canary_metrics

def test_promote():
    r = analyze_canary_metrics(
        {"error_rate": 0.5, "p99_ms": 200, "success_rate": 99.5},
        {"error_rate": 0.6, "p99_ms": 210, "success_rate": 99.4})
    assert r["verdict"] == "promote"
    assert r["confidence_pct"] == 100.0

def test_rollback():
    r = analyze_canary_metrics(
        {"error_rate": 0.5, "p99_ms": 200},
        {"error_rate": 5.0, "p99_ms": 400, "success_rate": 95})
    assert r["verdict"] == "rollback"

def test_hold():
    r = analyze_canary_metrics(
        {"error_rate": 0.5, "p99_ms": 200},
        {"error_rate": 0.5, "p99_ms": 300, "success_rate": 99})
    assert r["verdict"] == "hold"
