from app.services.app_marketplace_app_app_app_app_app_app_app_anomaly_detector import detect_anomalies

def test_anomalies():
    values = [10, 12, 11, 13, 10, 11, 50, 12, 10, 11]
    r = detect_anomalies(values, threshold=2.0, labels=["mon", "tue", "wed", "thu", "fri", "sat", "sun_spike", "mon2", "tue2", "wed2"])
    assert r["count"] == 1
    assert r["anomalies"][0]["label"] == "sun_spike"
    assert r["anomalies"][0]["value"] == 50
    assert r["anomalies"][0]["direction"] == "high"
    assert r["mean"] < 20

def test_no_anomalies():
    r = detect_anomalies([10, 10, 10, 10, 10])
    assert r["count"] == 0
