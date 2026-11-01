from app.services.app_marketplace_app_app_app_app_app_app_app_monitor_summary import monitoring_summary

def test_healthy():
    r = monitoring_summary({"uptime_pct": 99.99, "error_rate_pct": 0.1, "p99_ms": 100,
                             "rps": 5000, "cpu_pct": 40, "memory_pct": 50,
                             "active_alerts": 0, "open_incidents": 0})
    assert r["status"] == "healthy"
    assert r["score"] == 100

def test_critical():
    r = monitoring_summary({"uptime_pct": 95, "error_rate_pct": 10, "p99_ms": 2000,
                             "rps": 100, "cpu_pct": 95, "memory_pct": 90,
                             "active_alerts": 5, "open_incidents": 2})
    assert r["status"] == "critical"
    assert r["score"] < 50
