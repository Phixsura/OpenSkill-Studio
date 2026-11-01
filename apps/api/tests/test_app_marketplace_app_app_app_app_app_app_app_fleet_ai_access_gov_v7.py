from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_access_gov_v7 import fleet_ai_access_governance_v7
def test_agv7():
    r = fleet_ai_access_governance_v7([{"active": True, "users": 100000, "roles": 500, "reviews": 200, "excessive": 0}])
    assert r["users"] == 100000
    assert r["clean"]
