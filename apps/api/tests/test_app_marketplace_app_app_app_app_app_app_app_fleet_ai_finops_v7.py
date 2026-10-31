from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_finops_v7 import fleet_ai_finops_v7
def test_fv7():
    r = fleet_ai_finops_v7([{"active": True, "spend_usd": 10000000, "savings_usd": 4000000, "cost_per_req": 0.00001}])
    assert r["roi"] == 40.0
    assert r["optimized"]
