from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_finops import fleet_finops_score
def test_finops():
    r = fleet_finops_score({"cost_visibility_pct": 90, "optimization_pct": 80, "governance_pct": 70})
    assert r["score"] == 80.0
    assert r["level"] == "Run"
