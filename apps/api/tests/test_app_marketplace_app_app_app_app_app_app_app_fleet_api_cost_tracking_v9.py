from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_cost_tracking_v9 import fleet_api_cost_tracking_v9
def test_act2_v9():
    r = fleet_api_cost_tracking_v9([{"monthly_cost": 5000, "calls_monthly": 10000000, "budget": 10000}])
    assert r["over_budget"] == 0
    assert r["healthy"]
