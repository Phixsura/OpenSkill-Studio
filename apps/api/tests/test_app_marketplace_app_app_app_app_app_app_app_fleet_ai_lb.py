from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_lb import fleet_ai_lb
def test_lb():
    r = fleet_ai_lb([{"active": True, "rps": 100000, "backends": 20}])
    assert r["rps"] == 100000
    assert r["all_active"]
