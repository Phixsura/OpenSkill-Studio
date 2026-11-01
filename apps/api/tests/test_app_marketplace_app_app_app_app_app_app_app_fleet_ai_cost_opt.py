from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_cost_opt import fleet_ai_cost_optimizer
def test_co():
    r = fleet_ai_cost_optimizer([{"active": True, "monthly_spend": 50000, "savings": 20000}])
    assert r["savings"] == 20000
    assert r["optimized"]
