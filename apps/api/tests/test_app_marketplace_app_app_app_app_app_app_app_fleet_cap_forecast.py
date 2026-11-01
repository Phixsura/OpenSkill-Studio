from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_cap_forecast import fleet_capacity_forecast
def test_forecast():
    r = fleet_capacity_forecast(80, 1.0)
    assert r["days_until_full"] == 20.0
    assert r["urgent"]
def test_no_growth():
    r = fleet_capacity_forecast(50, 0)
    assert r["days_until_full"] == -1
    assert not r["urgent"]
