from app.services.app_marketplace_app_api_health_probe import run_health_probes

def test_all_healthy():
    services = [
        {"name": "API", "latency_ms": 20, "checks": [{"name": "db", "status": "pass"}, {"name": "cache", "status": "pass"}]},
        {"name": "Worker", "latency_ms": 10, "checks": [{"name": "queue", "status": "pass"}]},
    ]
    r = run_health_probes(services=services)
    assert r["all_healthy"]
    assert r["overall_status"] == "healthy"
    assert r["healthy_count"] == 2

def test_degraded():
    services = [
        {"name": "API", "checks": [{"name": "db", "status": "pass"}]},
        {"name": "Search", "checks": [{"name": "index", "status": "fail"}]},
    ]
    r = run_health_probes(services=services)
    assert not r["all_healthy"]
    assert r["overall_status"] == "degraded"
