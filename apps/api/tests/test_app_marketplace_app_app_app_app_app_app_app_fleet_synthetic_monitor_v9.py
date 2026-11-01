from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_synthetic_monitor_v9 import fleet_synthetic_monitor_v9
def test_sm_v9():
    r = fleet_synthetic_monitor_v9([{"passing": True, "duration_ms": 250}])
    assert r["passing"] == 1
    assert r["healthy"]
