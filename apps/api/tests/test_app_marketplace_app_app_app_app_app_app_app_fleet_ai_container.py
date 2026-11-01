from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_container import fleet_ai_container
def test_ct():
    r = fleet_ai_container([{"active": True, "containers": 500, "images": 100, "startup_s": 3}])
    assert r["containers"] == 500
    assert r["fast"]
