from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_cost_forecast import fleet_cost_forecast
def test_forecast():
    r = fleet_cost_forecast(2000)
    assert r["monthly"] == 60000
    assert r["annual"] == 720000
    assert r["budget_warning"]
