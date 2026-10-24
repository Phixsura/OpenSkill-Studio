from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_timeseries import fleet_ai_timeseries
def test_ts():
    r = fleet_ai_timeseries([{"active": True, "forecasts_24h": 500000, "mape": 4.5, "horizon_days": 90}])
    assert r["mape"] == 4.5
    assert r["accurate"]
