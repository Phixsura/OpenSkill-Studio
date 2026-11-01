from app.services.app_marketplace_app_developer_app_metric_alerts_v2 import compute_dynamic_threshold, detect_anomaly, build_alert_history

def test_threshold():
    values = [100, 102, 98, 101, 99, 100, 103, 97]
    t = compute_dynamic_threshold(values=values)
    assert t["mean"] == 100.0
    assert t["upper"] > 100
    assert t["lower"] < 100

def test_anomaly_above():
    threshold = {"mean": 100, "std": 5, "upper": 110, "lower": 90}
    r = detect_anomaly(value=120, threshold=threshold)
    assert r["is_anomaly"]
    assert r["direction"] == "above"

def test_normal():
    threshold = {"mean": 100, "std": 5, "upper": 110, "lower": 90}
    r = detect_anomaly(value=102, threshold=threshold)
    assert not r["is_anomaly"]

def test_history():
    alerts = [{"is_anomaly": True, "timestamp": "2026-01-01"}, {"is_anomaly": False, "timestamp": "2026-01-02"}]
    r = build_alert_history(alerts=alerts)
    assert r["anomaly_count"] == 1
    assert r["anomaly_rate"] == 50.0
