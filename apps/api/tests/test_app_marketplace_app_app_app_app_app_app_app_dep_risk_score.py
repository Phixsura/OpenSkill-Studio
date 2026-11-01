from app.services.app_marketplace_app_app_app_app_app_app_app_dep_risk_score import score_risk, rank_services

def test_score():
    r = score_risk({"name": "api", "dependencies": ["db", "cache", "queue"],
                     "single_point_of_failure": True, "has_fallback": False,
                     "external_dependencies": 2})
    assert r["score"] > 80
    assert r["level"] == "critical"

def test_low_risk():
    r = score_risk({"name": "static", "dependencies": [],
                     "has_fallback": True, "external_dependencies": 0})
    assert r["level"] == "low"

def test_rank():
    ranked = rank_services([
        {"name": "low", "dependencies": [], "has_fallback": True},
        {"name": "high", "dependencies": ["a", "b", "c", "d", "e"],
         "single_point_of_failure": True, "external_dependencies": 3},
    ])
    assert ranked[0]["service"] == "high"
