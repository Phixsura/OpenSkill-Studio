from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_platform_vision_v8 import fleet_ai_vision_v8
def test_vv8():
    r = fleet_ai_vision_v8([{"active": True, "goals": 100, "achieved": 80, "years": 10}])
    assert r["achieved"] == 80
    assert r["visionary"]
