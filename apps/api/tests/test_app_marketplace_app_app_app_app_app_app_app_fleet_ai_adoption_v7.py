from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_adoption_v7 import fleet_ai_adoption_v7
def test_av7():
    r = fleet_ai_adoption_v7([{"active": True, "signups_30d": 50000, "activated": 25000, "retained": 20000}])
    assert r["conversion"] == 50.0
    assert r["growing"]
