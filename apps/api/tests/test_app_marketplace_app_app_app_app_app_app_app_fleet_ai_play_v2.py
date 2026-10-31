from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_play_v2 import fleet_ai_playground_v2
def test_pv2():
    r = fleet_ai_playground_v2([{"active": True, "sessions_24h": 100000, "shared": 20000, "satisfaction": 4.8}])
    assert r["sessions_24h"] == 100000
    assert r["loved"]
