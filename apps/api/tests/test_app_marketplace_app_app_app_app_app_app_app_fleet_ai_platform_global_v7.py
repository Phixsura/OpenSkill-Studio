from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_platform_global_v7 import fleet_ai_global_v7
def test_gv7():
    r = fleet_ai_global_v7([{"active": True, "regions": 20, "countries": 100, "languages": 30}])
    assert r["countries"] == 100
    assert r["global"]
