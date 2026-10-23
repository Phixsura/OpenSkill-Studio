from app.services.app_marketplace_app_app_app_app_app_app_app_cost_anomaly import detect_cost_anomalies

def test_anomaly():
    data = [
        {"date": "2026-10-20", "amount": 100, "service": "compute"},
        {"date": "2026-10-21", "amount": 105, "service": "compute"},
        {"date": "2026-10-22", "amount": 98, "service": "compute"},
        {"date": "2026-10-23", "amount": 250, "service": "compute"},
        {"date": "2026-10-24", "amount": 102, "service": "compute"},
    ]
    r = detect_cost_anomalies(data, threshold_pct=50)
    assert r["has_anomalies"]
    assert r["count"] == 1
    assert r["anomalies"][0]["date"] == "2026-10-23"
    assert r["anomalies"][0]["amount"] == 250

def test_no_anomaly():
    data = [{"date": f"d{i}", "amount": 100} for i in range(5)]
    r = detect_cost_anomalies(data)
    assert not r["has_anomalies"]
