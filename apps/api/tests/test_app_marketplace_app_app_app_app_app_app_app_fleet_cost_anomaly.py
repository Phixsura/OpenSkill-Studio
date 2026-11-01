from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_cost_anomaly import detect_cost_anomaly
def test_anomaly():
    r = detect_cost_anomaly([100, 100, 100, 100, 500])
    assert r["anomaly"]
    assert r["ratio"] == 5.0
def test_normal():
    r = detect_cost_anomaly([100, 100, 100, 110])
    assert not r["anomaly"]
