from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_videogen import fleet_ai_videogen
def test_vg():
    r = fleet_ai_videogen([{"active": True, "videos_24h": 50000, "minutes_24h": 100000}])
    assert r["videos_24h"] == 50000
    assert r["all_active"]
