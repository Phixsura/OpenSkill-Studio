from app.services.app_marketplace_complete_platform_health_final import build_platform_health_final

def test_healthy():
    p = build_platform_health_final(
        services=[{"name": "API", "status": "healthy"}, {"name": "CDN", "status": "healthy"}],
        uptime={"pct": 99.99}, error_budget={"remaining": 80},
        incidents=[], deployment={"latest": "v3.0"}, infrastructure={"regions": 4})
    assert p["overall"] == "healthy"
    assert p["healthy_count"] == 2

def test_degraded():
    p = build_platform_health_final(
        services=[{"name": "API", "status": "healthy"}, {"name": "CDN", "status": "degraded"}],
        uptime={}, error_budget={}, incidents=[{"status": "investigating"}],
        deployment={}, infrastructure={})
    assert p["overall"] == "degraded"
    assert len(p["active_incidents"]) == 1
