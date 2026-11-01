from app.services.app_marketplace_app_app_app_app_app_app_app_canary_analysis import analyze_canary, canary_recommendation

def test_pass():
    r = analyze_canary({"error_rate": 1.0, "p99_ms": 200}, {"error_rate": 1.05, "p99_ms": 205})
    assert r["verdict"] == "pass"
    assert not r["has_regression"]

def test_fail():
    r = analyze_canary({"error_rate": 1.0, "p99_ms": 200}, {"error_rate": 5.0, "p99_ms": 500})
    assert r["verdict"] == "fail"
    assert r["has_regression"]

def test_recommendation():
    analysis = analyze_canary({"error_rate": 1.0}, {"error_rate": 5.0})
    r = canary_recommendation(analysis)
    assert r["action"] == "rollback"
    assert "error_rate" in r["regressions"]
