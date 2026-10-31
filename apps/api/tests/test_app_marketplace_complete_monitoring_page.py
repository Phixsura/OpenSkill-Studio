from app.services.app_marketplace_complete_monitoring_page import build_complete_monitoring_page

def test_healthy():
    p = build_complete_monitoring_page(
        app={"id": "a1", "name": "App"}, metrics={"cpu": 30},
        alerts=[], uptime={"pct": 99.99}, error_budget={"remaining": 50},
        health_checks=[{"status": "pass"}])
    assert p["health"] == "healthy"

def test_critical():
    alerts = [{"triggered": True}] * 5
    p = build_complete_monitoring_page(
        app={"id": "a1", "name": "App"}, metrics={}, alerts=alerts,
        uptime={}, error_budget={}, health_checks=[])
    assert p["health"] == "critical"
