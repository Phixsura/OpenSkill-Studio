from app.services.app_marketplace_app_app_app_app_app_app_app_health_dash_agg import aggregate_health_dashboard

def test_healthy():
    r = aggregate_health_dashboard({"uptime_pct": 99.99, "error_rate_pct": 0.1,
                                     "p99_ms": 100, "cpu_pct": 40, "deps_healthy": True})
    assert r["status"] == "healthy"
    assert r["score"] == 100

def test_critical():
    r = aggregate_health_dashboard({"uptime_pct": 95, "error_rate_pct": 10,
                                     "p99_ms": 2000, "cpu_pct": 95, "deps_healthy": False})
    assert r["status"] == "critical"
    assert r["passing"] == 0
