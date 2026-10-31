from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_platform_leadership_v7 import fleet_ai_platform_leadership_v7
def test_plv7():
    r = fleet_ai_platform_leadership_v7([{"active": True, "rank": 1, "awards": 50, "rating": 4.9}])
    assert r["rank"] == 1
    assert r["leader"]
