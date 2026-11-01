from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_liveness import fleet_ai_liveness
def test_lv():
    r = fleet_ai_liveness([{"active": True, "services": 500, "alive": 500, "restarts": 2}])
    assert r["alive"] == 500
    assert r["stable"]
