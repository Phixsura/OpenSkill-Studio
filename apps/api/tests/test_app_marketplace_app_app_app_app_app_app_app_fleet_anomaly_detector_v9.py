from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_anomaly_detector_v9 import fleet_anomaly_detector_v9
def test_ad_v9():
    r = fleet_anomaly_detector_v9([{"active": True, "anomalies_found": 100, "false_positives": 5}])
    assert r["anomalies"] == 100
    assert r["healthy"]
