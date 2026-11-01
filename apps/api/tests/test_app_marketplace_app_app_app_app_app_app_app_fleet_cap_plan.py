from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_cap_plan import fleet_capacity_planning
def test_plan():
    r = fleet_capacity_planning([{"utilization_forecast_pct": 90, "cost_delta_usd": 5000}, {"utilization_forecast_pct": 50}])
    assert r["needs_expansion"] == 1
    assert r["cost_delta_usd"] == 5000
    assert r["action_needed"]
