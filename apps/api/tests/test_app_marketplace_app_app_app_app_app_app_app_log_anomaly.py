from app.services.app_marketplace_app_app_app_app_app_app_app_log_anomaly import detect_log_anomalies

def test_spike():
    counts = [100, 105, 98, 102, 500, 101, 99]  # 500 is anomaly
    r = detect_log_anomalies(counts)
    assert r["has_anomaly"]
    assert any(a["type"] == "spike" for a in r["anomalies"])

def test_normal():
    counts = [100, 102, 98, 101, 103, 99]
    r = detect_log_anomalies(counts)
    assert not r["has_anomaly"]
