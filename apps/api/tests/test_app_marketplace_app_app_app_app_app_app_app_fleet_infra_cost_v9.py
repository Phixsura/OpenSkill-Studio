from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_infra_cost_v9 import fleet_infra_cost_v9
def test_ic_v9():
    r = fleet_infra_cost_v9([{"monthly_cost": 5000, "budget": 10000}, {"monthly_cost": 3000, "budget": 5000}])
    assert r["total_monthly"] == 8000
    assert r["over_budget"] == 0
    assert r["healthy"]
