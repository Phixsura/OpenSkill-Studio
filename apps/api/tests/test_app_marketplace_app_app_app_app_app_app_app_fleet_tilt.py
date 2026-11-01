from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_tilt import fleet_tilt_status
def test_tilt():
    r = fleet_tilt_status([{"status": "running", "resources": 20, "avg_update_ms": 1500}])
    assert r["resources"] == 20
    assert r["fast"]
