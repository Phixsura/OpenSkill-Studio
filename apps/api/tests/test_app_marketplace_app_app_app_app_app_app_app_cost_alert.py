from app.services.app_marketplace_app_app_app_app_app_app_app_cost_alert import check_cost_anomaly, cost_alert_summary

def test_spike():
    r = check_cost_anomaly([100, 105, 98, 102, 99], 500)
    assert r["anomaly"]
    assert r["type"] == "spike"
    assert r["alert"]

def test_normal():
    r = check_cost_anomaly([100, 105, 98, 102, 99], 103)
    assert not r["anomaly"]

def test_summary():
    alerts = [{"anomaly": True, "type": "spike"}, {"anomaly": False, "type": "normal"}]
    r = cost_alert_summary(alerts)
    assert r["spikes"] == 1
    assert r["any_alert"]
