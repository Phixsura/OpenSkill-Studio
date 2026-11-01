from app.services.app_marketplace_app_app_app_app_app_app_app_alert_rule import evaluate_alert, alert_summary

def test_fire():
    alerts = evaluate_alert("cpu_pct", 95, [
        {"name": "high_cpu", "metric": "cpu_pct", "operator": ">", "threshold": 80, "severity": "warning"},
        {"name": "critical_cpu", "metric": "cpu_pct", "operator": ">", "threshold": 90, "severity": "critical"},
    ])
    assert len(alerts) == 2

def test_no_fire():
    alerts = evaluate_alert("cpu_pct", 50, [
        {"name": "high_cpu", "metric": "cpu_pct", "operator": ">", "threshold": 80},
    ])
    assert len(alerts) == 0

def test_summary():
    r = alert_summary([
        {"severity": "warning"}, {"severity": "critical"}, {"severity": "warning"},
    ])
    assert r["total"] == 3
    assert r["has_critical"]
