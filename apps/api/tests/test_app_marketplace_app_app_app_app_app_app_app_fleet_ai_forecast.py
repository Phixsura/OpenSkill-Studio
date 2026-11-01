from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_forecast import fleet_ai_forecast
def test_fc():
    r = fleet_ai_forecast([{"active": True, "predictions_24h": 1000000, "mape_pct": 5}])
    assert r["predictions_24h"] == 1000000
    assert r["accurate"]
