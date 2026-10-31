from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_policy_eng import fleet_ai_policy_engine
def test_pe():
    r = fleet_ai_policy_engine([{"active": True, "policies": 100, "evals_24h": 50000000, "violations": 0}])
    assert r["policies"] == 100
    assert r["compliant"]
