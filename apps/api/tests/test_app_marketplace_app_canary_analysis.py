from app.services.app_marketplace_app_canary_analysis import analyze_canary

def test_promote():
    r = analyze_canary(
        baseline={"error_rate": 0.1, "p95_latency_ms": 100, "success_rate": 99.9},
        canary={"error_rate": 0.2, "p95_latency_ms": 110, "success_rate": 99.8})
    assert r["verdict"] == "promote"
    assert r["confidence"] == 100

def test_rollback():
    r = analyze_canary(
        baseline={"error_rate": 0.1, "p95_latency_ms": 100},
        canary={"error_rate": 2.0, "p95_latency_ms": 300, "success_rate": 95.0})
    assert r["verdict"] == "rollback"
    assert r["passed"] < r["total"]
