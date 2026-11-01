from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_config_drift_v9 import fleet_config_drift_v9
def test_drift_v9():
    r = fleet_config_drift_v9([{"drifted": False}, {"drifted": False}])
    assert r["synced"] == 2
    assert r["drift_pct"] == 0.0
    assert r["healthy"]
