from app.services.app_marketplace_app_app_app_app_app_app_app_dep_health import check_dependency_health, suggest_alternatives

def test_health():
    r = check_dependency_health([
        {"name": "postgres", "status": "healthy"},
        {"name": "redis", "status": "degraded"},
        {"name": "external-api", "status": "down"},
    ])
    assert r["healthy"] == 1
    assert r["down"] == 1
    assert not r["all_healthy"]

def test_alternatives():
    r = suggest_alternatives({"name": "redis"})
    assert r["has_alternatives"]
    assert "memcached" in r["alternatives"]
