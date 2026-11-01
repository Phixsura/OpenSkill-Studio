from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_avatar import fleet_ai_avatar
def test_av():
    r = fleet_ai_avatar([{"active": True, "avatars_24h": 50000, "animations_24h": 200000}])
    assert r["avatars_24h"] == 50000
    assert r["all_active"]
