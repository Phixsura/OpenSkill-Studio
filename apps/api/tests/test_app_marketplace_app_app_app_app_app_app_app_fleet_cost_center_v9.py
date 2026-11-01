from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_cost_center_v9 import fleet_cost_center_v9
def test_cc2_v9():
    r = fleet_cost_center_v9([{"monthly_spend": 20000, "budget": 30000, "teams": 5}])
    assert r["over_budget"] == 0
    assert r["healthy"]
