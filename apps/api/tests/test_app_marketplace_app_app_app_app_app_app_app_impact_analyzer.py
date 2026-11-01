from app.services.app_marketplace_app_app_app_app_app_app_app_impact_analyzer import analyze_impact, risk_ranking

def test_impact():
    graph = {"api": ["db", "cache"], "web": ["api"], "worker": ["db", "api"], "db": [], "cache": []}
    r = analyze_impact("db", graph)
    assert "api" in r["affected_services"]
    assert "worker" in r["affected_services"]
    assert r["blast_radius"] >= 3  # api, web, worker depend on db

def test_ranking():
    graph = {"api": ["db"], "web": ["api"], "worker": ["db"], "db": [], "cache": []}
    rankings = risk_ranking(graph)
    assert rankings[0]["service"] == "db"  # highest blast radius
