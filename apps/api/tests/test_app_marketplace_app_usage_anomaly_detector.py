from app.services.app_marketplace_app_usage_anomaly_detector import detect_anomalies

def test_detect():
    data = [100, 102, 98, 101, 99, 100, 500, 101, 98, 100]  # 500 is anomaly
    r = detect_anomalies(data_points=data, sensitivity=2.0)
    assert r["anomaly_count"] >= 1
    assert any(a["value"] == 500 for a in r["anomalies"])
    assert r["anomalies"][0]["type"] == "spike"

def test_no_anomalies():
    data = [100, 101, 99, 100, 102, 98, 101, 100, 99, 101]
    r = detect_anomalies(data_points=data, sensitivity=3.0)
    assert r["anomaly_count"] == 0

def test_too_few():
    r = detect_anomalies(data_points=[1, 2, 3])
    assert "error" in r
