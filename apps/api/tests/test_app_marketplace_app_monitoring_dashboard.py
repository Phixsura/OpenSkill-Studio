from app.services.app_marketplace_app_monitoring_dashboard import build_monitoring_dashboard

def test_healthy():
    d = build_monitoring_dashboard(app={"id": "a1", "name": "App"}, metrics={"cpu": 30},
                                    alerts=[], uptime_history=[{"date": "2026-01-01", "pct": 99.99}])
    assert d["health"] == "healthy"
    assert len(d["panels"]) == 4

def test_critical():
    alerts = [{"triggered": True}] * 5
    d = build_monitoring_dashboard(app={"id": "a1", "name": "App"}, metrics={}, alerts=alerts, uptime_history=[])
    assert d["health"] == "critical"
