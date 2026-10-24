from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_cost_trend import fleet_cost_trend
def test_increasing():
    r = fleet_cost_trend([{"cost": 10000}, {"cost": 12000}])
    assert r["trend"] == "increasing"
    assert r["change_pct"] == 20.0
