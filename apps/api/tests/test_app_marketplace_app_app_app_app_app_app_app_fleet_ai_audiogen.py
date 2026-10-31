from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_audiogen import fleet_ai_audiogen
def test_ag():
    r = fleet_ai_audiogen([{"active": True, "clips_24h": 100000, "hours_24h": 5000}])
    assert r["clips_24h"] == 100000
    assert r["all_active"]
