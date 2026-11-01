from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_cost import fleet_ai_cost
def test_aic():
    r = fleet_ai_cost([{"monthly_cost": 50000, "gpu_cost": 30000, "inference_cost": 20000, "savings_available": 3000}])
    assert r["total_monthly"] == 50000
    assert r["optimized"]
