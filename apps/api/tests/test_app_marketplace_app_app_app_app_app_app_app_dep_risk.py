from app.services.app_marketplace_app_app_app_app_app_app_app_dep_risk import assess_dependency_risk

def test_risk():
    deps = {
        "web": {"depends_on": ["api"]},
        "api": {"depends_on": ["db", "cache", "auth"]},
        "auth": {"depends_on": ["db"]},
        "db": {"depends_on": []},
        "cache": {"depends_on": []},
    }
    r = assess_dependency_risk("web", deps)
    assert r["direct_deps"] == 1
    assert r["transitive_deps"] == 4  # api, db, cache, auth
    assert r["max_depth"] == 3  # web→api→auth→db
    assert r["risk_level"] in ("high", "critical")
