from app.services.app_marketplace_app_alert_rules import create_alert_rule, evaluate_alert, build_alert_summary

def test_create():
    r = create_alert_rule(app_id="a1", name="High errors", metric="error_rate",
                           operator="gt", threshold=5.0, notify_channels=["email"])
    assert r["status"] == "active"

def test_invalid_metric():
    r = create_alert_rule(app_id="a1", name="X", metric="magic", operator="gt", threshold=1, notify_channels=[])
    assert r["error"]

def test_triggered():
    rule = {"name": "High CPU", "metric": "cpu_usage", "operator": "gt", "threshold": 80}
    r = evaluate_alert(rule=rule, current_value=95)
    assert r["triggered"]

def test_not_triggered():
    rule = {"name": "Low errors", "metric": "error_rate", "operator": "gt", "threshold": 5}
    r = evaluate_alert(rule=rule, current_value=2)
    assert not r["triggered"]

def test_summary():
    alerts = [{"triggered": True, "metric": "error_rate"}, {"triggered": False, "metric": "cpu_usage"},
              {"triggered": True, "metric": "response_time"}]
    s = build_alert_summary(alerts=alerts)
    assert s["active_alerts"] == 2
    assert len(s["critical"]) == 1
