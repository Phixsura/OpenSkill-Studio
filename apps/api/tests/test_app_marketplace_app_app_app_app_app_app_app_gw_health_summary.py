from app.services.app_marketplace_app_app_app_app_app_app_app_gw_health_summary import gateway_health_summary

def test_healthy():
    r = gateway_health_summary({"rps": 5000, "error_rate_pct": 0.1, "p99_ms": 100,
                                 "uptime_pct": 99.99, "active_connections": 1000, "max_connections": 10000})
    assert r["status"] == "healthy"
    assert r["score"] == 100

def test_degraded():
    r = gateway_health_summary({"rps": 5000, "error_rate_pct": 5, "p99_ms": 800,
                                 "uptime_pct": 99.5, "active_connections": 9000, "max_connections": 10000})
    assert r["status"] == "critical"
