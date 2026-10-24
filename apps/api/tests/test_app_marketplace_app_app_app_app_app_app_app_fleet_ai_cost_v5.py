from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_cost_v5 import fleet_ai_cost_v5
def test_cv5():
    r = fleet_ai_cost_v5([{"active": True, "total_usd": 5000000, "savings_usd": 2000000, "forecast_acc": 95}])
    assert r["savings_usd"] == 2000000
    assert r["optimized"]
