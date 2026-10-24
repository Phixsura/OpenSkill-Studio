from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_platform_unit_economics_v8 import fleet_ai_unit_economics_v8
def test_uev8():
    r = fleet_ai_unit_economics_v8([{"active": True, "ltv_usd": 100000, "cac_usd": 10000, "payback_m": 6}])
    assert r["ltv_cac"] == 10.0
    assert r["efficient"]
