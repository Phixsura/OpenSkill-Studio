from app.services.app_marketplace_app_app_app_app_app_app_app_health_compare import compare_health

def test_improved():
    r = compare_health(
        {"service": "api", "uptime_pct": 99.99, "error_rate_pct": 0.1, "p99_ms": 80, "incidents": 0},
        {"service": "api", "uptime_pct": 99.5, "error_rate_pct": 1.0, "p99_ms": 200, "incidents": 3})
    assert r["overall"] == "improved"

def test_degraded():
    r = compare_health(
        {"service": "api", "uptime_pct": 98, "error_rate_pct": 5, "p99_ms": 500, "incidents": 5},
        {"service": "api", "uptime_pct": 99.9, "error_rate_pct": 0.1, "p99_ms": 100, "incidents": 1})
    assert r["overall"] == "degraded"
