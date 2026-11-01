from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_capacity_forecast_v9 import fleet_capacity_forecast_v9
def test_cf_v9():
    r = fleet_capacity_forecast_v9([{"days_to_capacity": 90, "growth_pct_monthly": 5, "projected_monthly_cost": 10000}])
    assert r["at_risk_30d"] == 0
    assert r["healthy"]
