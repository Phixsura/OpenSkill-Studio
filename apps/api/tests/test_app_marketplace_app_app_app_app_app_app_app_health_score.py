from app.services.app_marketplace_app_app_app_app_app_app_app_health_score import calculate_health_score

def test_healthy():
    r = calculate_health_score({"uptime_pct": 99.99, "error_rate_pct": 0.1,
                                "p99_ms": 50, "cpu_pct": 40, "data_age_minutes": 5})
    assert r["grade"] == "A"
    assert r["score"] >= 90

def test_unhealthy():
    r = calculate_health_score({"uptime_pct": 95, "error_rate_pct": 10,
                                "p99_ms": 2000, "cpu_pct": 95, "data_age_minutes": 60})
    assert r["grade"] in ("D", "F")
