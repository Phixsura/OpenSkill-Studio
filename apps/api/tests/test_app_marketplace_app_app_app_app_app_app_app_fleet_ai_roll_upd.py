from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_roll_upd import fleet_ai_rolling_update
def test_ru():
    r = fleet_ai_rolling_update([{"active": True, "updates_24h": 30, "instances": 500, "rollbacks": 0}])
    assert r["instances"] == 500
    assert r["smooth"]
