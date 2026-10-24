from app.services.app_marketplace_app_app_app_app_app_app_app_canary_deploy import analyze_canary

def test_promote():
    r = analyze_canary(
        {"error_rate": 0.1, "p99_ms": 200, "requests": 10000},
        {"error_rate": 0.12, "p99_ms": 210, "requests": 1000})
    assert r["verdict"] == "promote"

def test_rollback():
    r = analyze_canary(
        {"error_rate": 0.1, "p99_ms": 200, "requests": 10000},
        {"error_rate": 2.0, "p99_ms": 500, "requests": 1000})
    assert r["verdict"] == "rollback"

def test_hold():
    r = analyze_canary(
        {"error_rate": 0.1, "p99_ms": 200, "requests": 10000},
        {"error_rate": 0.1, "p99_ms": 300, "requests": 1000})
    assert r["verdict"] == "hold"
