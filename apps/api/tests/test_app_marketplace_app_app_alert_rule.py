from app.services.app_marketplace_app_app_alert_rule import evaluate_alert, build_alert_rules

def test_triggered():
    r = evaluate_alert(metric_value=95, threshold=90, operator="gt")
    assert r["triggered"]
    assert r["status"] == "firing"

def test_ok():
    r = evaluate_alert(metric_value=50, threshold=90, operator="gt")
    assert not r["triggered"]
    assert r["status"] == "ok"

def test_lt():
    r = evaluate_alert(metric_value=5, threshold=10, operator="lt")
    assert r["triggered"]

def test_rules():
    rules = [
        {"name": "High CPU", "metric": "cpu_pct", "operator": "gt", "threshold": 80, "status": "firing"},
        {"name": "Low Disk", "metric": "disk_pct", "operator": "lt", "threshold": 10, "status": "ok"},
    ]
    r = build_alert_rules(rules=rules)
    assert r["total"] == 2
    assert r["firing"] == 1
    assert not r["healthy"]
