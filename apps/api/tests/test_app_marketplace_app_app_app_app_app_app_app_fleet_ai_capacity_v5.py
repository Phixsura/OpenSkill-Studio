from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_capacity_v5 import fleet_ai_capacity_v5
def test_cv5():
    r = fleet_ai_capacity_v5([{"active": True, "gpus": 50000, "headroom_pct": 35, "forecast_days": 365}])
    assert r["gpus"] == 50000
    assert r["prepared"]
