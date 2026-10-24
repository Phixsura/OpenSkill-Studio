from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_plat_cap_v3 import fleet_ai_platform_capacity_v3
def test_pcv3():
    r = fleet_ai_platform_capacity_v3([{"active": True, "forecasts": 500, "accuracy_pct": 95, "headroom_pct": 35}])
    assert r["accuracy"] == 95.0
    assert r["prepared"]
