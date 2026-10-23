from app.services.app_marketplace_app_app_app_app_app_app_app_cost_anomaly import detect_anomalies, estimate_savings

def test_detect():
    costs = [100, 102, 98, 101, 99, 500, 100, 101]  # 500 is anomaly
    r = detect_anomalies(costs)
    assert r["has_anomaly"]
    assert r["anomaly_count"] >= 1
    assert any(a["cost"] == 500 for a in r["anomalies"])

def test_no_anomaly():
    costs = [100, 101, 99, 100, 102]
    r = detect_anomalies(costs)
    assert not r["has_anomaly"]

def test_savings():
    anomalies = [{"cost": 500, "direction": "spike"}, {"cost": 20, "direction": "drop"}]
    r = estimate_savings(anomalies, 100)
    assert r["potential_savings"] == 400.0
    assert r["spike_count"] == 1
