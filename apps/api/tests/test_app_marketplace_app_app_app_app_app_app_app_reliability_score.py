from app.services.app_marketplace_app_app_app_app_app_app_app_reliability_score import calculate_reliability

def test_high():
    r = calculate_reliability({"service": "api", "uptime_pct": 99.99, "error_rate_pct": 0.1,
                                "p99_ms": 100, "mttr_minutes": 5, "incidents_30d": 1})
    assert r["grade"] == "A"
    assert r["score"] > 90

def test_low():
    r = calculate_reliability({"service": "legacy", "uptime_pct": 95, "error_rate_pct": 10,
                                "p99_ms": 2000, "mttr_minutes": 120, "incidents_30d": 10})
    assert r["grade"] == "F"
    assert r["score"] < 60
