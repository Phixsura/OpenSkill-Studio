from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_cost_forecast_v9 import fleet_cost_forecast_v9
def test_cf3_v9():
    r = fleet_cost_forecast_v9([{"variance_pct": 3, "forecast_amount": 50000, "actual_amount": 51500}])
    assert r["accurate"] == 1
    assert r["healthy"]
