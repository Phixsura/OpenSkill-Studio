from app.services.app_marketplace_platform_health_dashboard import build_platform_health_dashboard

def test_healthy():
    d = build_platform_health_dashboard(
        services=[{"name": "API", "status": "healthy"}, {"name": "Webhooks", "status": "healthy"}],
        app_count=500, active_installs=2000, error_rate=0.1, avg_response_ms=120)
    assert d["overall"] == "healthy"
    assert len(d["actions"]) == 0

def test_degraded():
    d = build_platform_health_dashboard(
        services=[{"name": "API", "status": "degraded"}],
        app_count=500, active_installs=2000, error_rate=3, avg_response_ms=500)
    assert d["overall"] == "degraded"
    assert len(d["actions"]) > 0
