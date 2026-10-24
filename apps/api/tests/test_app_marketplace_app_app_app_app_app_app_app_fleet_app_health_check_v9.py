from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_app_health_check_v9 import fleet_app_health_check_v9
def test_ahc_v9():
    r = fleet_app_health_check_v9([{"type": "liveness", "passing": True}, {"type": "readiness", "passing": True}])
    assert r["liveness_ok"] == 1
    assert r["healthy"]
