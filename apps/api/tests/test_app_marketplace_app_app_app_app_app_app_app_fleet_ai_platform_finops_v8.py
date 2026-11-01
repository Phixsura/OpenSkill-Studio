from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_platform_finops_v8 import fleet_ai_finops_v8
def test_fv8():
    r = fleet_ai_finops_v8([{"active": True, "spend_usd": 50000000, "savings_usd": 20000000, "cost_per_req": 0.0000005}])
    assert r["savings"] == 20000000
    assert r["optimized"]
