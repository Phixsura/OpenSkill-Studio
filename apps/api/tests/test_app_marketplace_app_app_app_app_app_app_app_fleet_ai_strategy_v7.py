from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_strategy_v7 import fleet_ai_strategy_v7
def test_sv7():
    r = fleet_ai_strategy_v7([{"active": True, "initiatives": 50, "completed": 40, "okrs": 20, "on_track_pct": 90}])
    assert r["initiatives"] == 50
    assert r["executing"]
