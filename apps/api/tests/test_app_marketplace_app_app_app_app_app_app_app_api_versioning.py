from app.services.app_marketplace_app_app_app_app_app_app_app_api_versioning import ApiVersionManager

def test_versioning():
    mgr = ApiVersionManager()
    mgr.register_version("v1", status="stable", endpoints=["/users", "/apps"])
    mgr.register_version("v2", status="stable", endpoints=["/users", "/apps", "/exports"])
    mgr.deprecate("v1", sunset_date="2027-01-01", migrate_to="v2")
    r = mgr.resolve("v1")
    assert r["status"] == "deprecated"
    assert "Migrate to v2" in r["warning"]
    r2 = mgr.resolve("v2")
    assert r2["status"] == "stable"
    s = mgr.summary()
    assert s["total"] == 2
    assert s["latest"] == "v2"

def test_fallback():
    mgr = ApiVersionManager()
    mgr.register_version("v1", status="stable")
    r = mgr.resolve("v99")
    assert r["fallback"]
    assert r["resolved"] == "v1"
