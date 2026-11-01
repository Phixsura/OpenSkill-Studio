from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_config_drift_detector_v9 import fleet_config_drift_detector_v9
def test_cdd_v9():
    r = fleet_config_drift_detector_v9([{"synced": True, "auto_remediated": False}])
    assert r["drifted"] == 0
    assert r["healthy"]
