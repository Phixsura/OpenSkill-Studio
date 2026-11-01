from app.services.app_marketplace_app_app_app_app_app_app_app_svc_catalog import ServiceCatalog

def test_register_search():
    cat = ServiceCatalog()
    cat.register("auth-svc", "team-a", "critical", ["auth", "security"])
    cat.register("user-svc", "team-b", "standard", ["users"])
    r = cat.search(tag="auth")
    assert len(r) == 1
    assert r[0]["name"] == "auth-svc"

def test_dependencies():
    cat = ServiceCatalog()
    cat.register("api", "team-a")
    cat.register("db", "team-b")
    cat.add_dependency("api", "db")
    assert "db" in cat.search(query="api")[0]["dependencies"]

def test_stats():
    cat = ServiceCatalog()
    cat.register("a", "t1", "critical")
    cat.register("b", "t1", "standard")
    s = cat.stats()
    assert s["total"] == 2
    assert s["by_tier"]["critical"] == 1
