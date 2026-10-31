from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_culture_v7 import fleet_ai_culture_v7
def test_cv7():
    r = fleet_ai_culture_v7([{"active": True, "enps": 72, "dx": 92, "hackathons": 12}])
    assert r["enps"] == 72
    assert r["thriving"]
