from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_drift_detector_v9 import fleet_drift_detector_v9
def test_dd_v9():
    r = fleet_drift_detector_v9([{"drifted": False, "auto_remediated": False}])
    assert r["drifted"] == 0
    assert r["healthy"]
