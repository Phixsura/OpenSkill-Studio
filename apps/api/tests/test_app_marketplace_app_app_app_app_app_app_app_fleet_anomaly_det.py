from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_anomaly_det import fleet_anomaly_detect
def test_anomaly():
    r = fleet_anomaly_detect([10, 10, 10, 10, 10, 100])
    assert r["anomalies"] == 1
    assert r["total"] == 6
