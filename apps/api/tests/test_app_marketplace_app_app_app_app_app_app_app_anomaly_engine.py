from app.services.app_marketplace_app_app_app_app_app_app_app_anomaly_engine import detect_anomalies

def test_detect():
    r = detect_anomalies({
        "cpu": [40, 42, 38, 41, 39, 95],  # 95 is anomaly
        "memory": [60, 62, 58, 61, 59, 60],  # stable
    })
    assert r["has_anomaly"]
    assert r["count"] == 1
    assert r["anomalies"][0]["metric"] == "cpu"

def test_no_anomaly():
    r = detect_anomalies({"x": [50, 51, 49, 50, 52]})
    assert not r["has_anomaly"]
