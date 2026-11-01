from app.services.app_platform_health_dashboard import build_health_dashboard

def test_healthy():
    d = build_health_dashboard(total_apps=50, healthy_apps=48, degraded_apps=2, critical_apps=0, avg_health=96, total_alerts=0)
    assert d["overall"] == "healthy"

def test_critical():
    d = build_health_dashboard(total_apps=50, healthy_apps=40, degraded_apps=5, critical_apps=5, avg_health=80, total_alerts=10)
    assert d["overall"] == "critical"

def test_degraded():
    d = build_health_dashboard(total_apps=50, healthy_apps=30, degraded_apps=20, critical_apps=0, avg_health=85, total_alerts=5)
    assert d["overall"] == "degraded"
