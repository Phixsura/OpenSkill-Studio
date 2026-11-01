from app.services.app_marketplace_app_app_app_health_monitor import build_health_monitor

def test_healthy():
    apps = [{"name": "A", "status": "healthy", "uptime_pct": 99.99, "response_ms": 45}]
    r = build_health_monitor(apps=apps)
    assert r["overall"] == "healthy"
    assert r["healthy"] == 1

def test_degraded():
    apps = [{"name": "A", "status": "healthy"}, {"name": "B", "status": "degraded"}]
    r = build_health_monitor(apps=apps)
    assert r["overall"] == "degraded"

def test_outage():
    apps = [{"name": "A", "status": "down"}]
    r = build_health_monitor(apps=apps)
    assert r["overall"] == "outage"
