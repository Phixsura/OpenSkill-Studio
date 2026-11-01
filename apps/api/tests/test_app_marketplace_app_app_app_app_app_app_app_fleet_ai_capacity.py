from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_capacity import fleet_ai_capacity
def test_cap():
    r = fleet_ai_capacity([{"active": True, "forecast_days": 90, "current_util": 65}])
    assert r["headroom_pct"] == 35.0
    assert r["safe"]
