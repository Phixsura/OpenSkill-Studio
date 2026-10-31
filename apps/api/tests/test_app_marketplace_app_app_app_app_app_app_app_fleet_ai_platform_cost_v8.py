from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_platform_cost_v8 import fleet_ai_cost_v8
def test_cv8():
    r = fleet_ai_cost_v8([{"active": True, "spend_usd": 20000000, "savings_usd": 8000000, "cost_per_req": 0.000001}])
    assert r["roi"] == 40.0
    assert r["optimized"]
