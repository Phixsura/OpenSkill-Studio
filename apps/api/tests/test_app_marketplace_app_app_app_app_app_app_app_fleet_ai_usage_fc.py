from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_usage_fc import fleet_ai_usage_forecast
def test_uf():
    r = fleet_ai_usage_forecast([{"active": True, "horizon_days": 90, "accuracy_pct": 92, "growth_pct": 25}])
    assert r["horizon_days"] == 90
    assert r["reliable"]
