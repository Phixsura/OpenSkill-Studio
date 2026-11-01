from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_platform_future_v8 import fleet_ai_future_v8
def test_fv8():
    r = fleet_ai_future_v8([{"active": True, "capabilities": 500, "research": 200, "prototypes": 50}])
    assert r["capabilities"] == 500
    assert r["forward"]
