from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_overview import fleet_overview

def test_healthy():
    r = fleet_overview([
        {"name": "api", "status": "healthy", "tier": "critical", "rps": 5000},
        {"name": "db", "status": "healthy", "tier": "critical", "rps": 3000},
        {"name": "cache", "status": "healthy", "tier": "standard", "rps": 8000},
    ])
    assert r["overall"] == "healthy"
    assert r["health_pct"] == 100.0
    assert r["total_rps"] == 16000

def test_degraded():
    svcs = [{"name": f"s{i}", "status": "healthy", "tier": "standard", "rps": 100} for i in range(8)]
    svcs += [{"name": "bad1", "status": "down", "tier": "critical", "rps": 0},
             {"name": "bad2", "status": "down", "tier": "standard", "rps": 0}]
    r = fleet_overview(svcs)
    assert r["overall"] == "degraded"
