from app.services.app_marketplace_app_app_app_app_app_app_app_dep_chain import analyze_chains

def test_chains():
    deps = {"web": ["api"], "api": ["auth", "db"], "auth": ["db"], "db": []}
    r = analyze_chains(deps)
    assert r["max_depth"] == 3  # web→api→auth→db
    assert r["service_count"] == 4
    assert "web" in r["critical_paths"]
