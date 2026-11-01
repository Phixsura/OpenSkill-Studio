from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_finops_v6 import fleet_ai_finops_v6
def test_fv6():
    r = fleet_ai_finops_v6([{"active": True, "spend_usd": 5000000, "savings_usd": 2000000, "cost_per_req": 0.00001}])
    assert r["savings"] == 2000000
    assert r["optimized"]
