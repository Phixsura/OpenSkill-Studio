from app.services.app_marketplace_app_app_app_app_app_app_app_dep_impact import analyze_impact, rank_criticality

def test_impact():
    deps = {"api": ["db", "cache"], "web": ["api"], "worker": ["db", "queue"]}
    r = analyze_impact("db", deps)
    assert "api" in r["affected_services"]
    assert "worker" in r["affected_services"]
    assert "web" in r["affected_services"]  # transitive via api
    assert r["blast_radius"] == 3

def test_rank():
    deps = {"api": ["db"], "web": ["api"], "worker": ["queue"]}
    ranked = rank_criticality(deps)
    assert ranked[0]["service"] == "db"  # highest blast radius
