from app.services.app_marketplace_app_health_dashboard import build_health_dashboard

def test_all_healthy():
    comps = [{"name": "API", "latency_ms": 50, "error_rate": 0.1},
             {"name": "DB", "latency_ms": 10, "error_rate": 0}]
    r = build_health_dashboard(components=comps)
    assert r["overall"] == "healthy"
    assert r["healthy"] == 2

def test_degraded():
    comps = [{"name": "API", "latency_ms": 50, "error_rate": 0.1},
             {"name": "Cache", "latency_ms": 2000, "error_rate": 8}]
    r = build_health_dashboard(components=comps)
    assert r["overall"] == "degraded"

def test_outage():
    comps = [{"name": "DB", "latency_ms": 5000, "error_rate": 50}]
    r = build_health_dashboard(components=comps)
    assert r["overall"] == "outage"
