from app.services.app_marketplace_app_billing_alert import create_alert, evaluate_alerts

def test_create():
    r = create_alert(app_id="a1", alert_type="monthly_spend", threshold=100.0, notify_channels=["email"])
    assert r["status"] == "active"
    assert r["threshold"] == 100.0

def test_create_invalid():
    r = create_alert(app_id="a1", alert_type="bad", threshold=50, notify_channels=[])
    assert "error" in r

def test_evaluate_triggered():
    alerts = [{"alert_id": "al1", "type": "monthly_spend", "threshold": 100}]
    r = evaluate_alerts(alerts=alerts, current_values={"monthly_spend": 120})
    assert r["triggered_count"] == 1
    assert r["triggered"][0]["severity"] == "warning"

def test_evaluate_clear():
    alerts = [{"alert_id": "al1", "type": "monthly_spend", "threshold": 100}]
    r = evaluate_alerts(alerts=alerts, current_values={"monthly_spend": 50})
    assert r["all_clear"]
