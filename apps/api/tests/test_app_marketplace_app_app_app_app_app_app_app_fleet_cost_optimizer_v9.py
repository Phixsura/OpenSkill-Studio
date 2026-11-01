from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_cost_optimizer_v9 import fleet_cost_optimizer_v9
def test_co_v9():
    r = fleet_cost_optimizer_v9([{"applied": True, "monthly_savings": 500}, {"applied": True, "monthly_savings": 300}])
    assert r["potential_savings"] == 800
    assert r["healthy"]
