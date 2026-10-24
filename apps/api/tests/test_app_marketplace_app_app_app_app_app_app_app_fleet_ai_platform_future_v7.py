from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_platform_future_v7 import fleet_ai_platform_future_v7
def test_pfv7():
    r = fleet_ai_platform_future_v7([{"active": True, "capabilities": 100, "research": 50, "prototypes": 20}])
    assert r["capabilities"] == 100
    assert r["forward_looking"]
