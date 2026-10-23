from app.services.app_marketplace_app_app_app_app_app_monitoring_page import build_monitoring_page

def test_healthy():
    r = build_monitoring_page(app_name="SuperApp", uptime_pct=99.99,
                               avg_latency_ms=45, error_rate_pct=0.1, active_users=500)
    assert r["health"] == "healthy"
    assert len(r["metrics"]) == 4
    assert r["alert_count"] == 0

def test_critical():
    r = build_monitoring_page(app_name="X", uptime_pct=95, avg_latency_ms=500,
                               error_rate_pct=8.5, active_users=10,
                               alerts=[{"title": "High error rate", "severity": "critical"}])
    assert r["health"] == "critical"
    assert r["alert_count"] == 1
