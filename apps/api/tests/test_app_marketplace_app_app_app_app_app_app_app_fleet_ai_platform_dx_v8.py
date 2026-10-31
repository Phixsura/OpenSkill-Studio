from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_platform_dx_v8 import fleet_ai_dx_v8
def test_dxv8():
    r = fleet_ai_dx_v8([{"active": True, "nps": 85, "ttfv_min": 2, "sat_pct": 98}])
    assert r["nps"] == 85
    assert r["world_class"]
