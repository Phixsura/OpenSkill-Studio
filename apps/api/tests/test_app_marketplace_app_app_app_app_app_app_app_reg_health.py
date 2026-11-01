from app.services.app_marketplace_app_app_app_app_app_app_app_reg_health import registry_health, detect_orphans

def test_health():
    r = registry_health([
        {"name": "api", "healthy": True}, {"name": "db", "healthy": True},
        {"name": "old", "stale": True}, {"name": "gone", "deregistered": True},
    ])
    assert r["healthy"] == 2
    assert r["stale"] == 1
    assert r["health_pct"] == 50.0

def test_orphans():
    r = detect_orphans(["api", "db", "old-svc"], ["api", "db", "new-svc"])
    assert "old-svc" in r["orphans"]
    assert "new-svc" in r["unregistered_deployments"]
    assert not r["clean"]
