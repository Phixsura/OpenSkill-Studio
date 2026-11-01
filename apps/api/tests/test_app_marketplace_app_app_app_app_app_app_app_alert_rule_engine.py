from app.services.app_marketplace_app_app_app_app_app_app_app_alert_rule_engine import create_rule, evaluate_rules

def test_evaluate():
    rules = [
        create_rule(name="High CPU", metric="cpu_pct", operator="gt", threshold=90, severity="critical"),
        create_rule(name="Low Disk", metric="disk_free_gb", operator="lt", threshold=10, severity="warning"),
        create_rule(name="Memory OK", metric="mem_pct", operator="gt", threshold=95, severity="info"),
    ]
    metrics = {"cpu_pct": 95, "disk_free_gb": 5, "mem_pct": 70}
    r = evaluate_rules(rules, metrics)
    assert r["count"] == 2
    assert r["highest_severity"] == "critical"
    assert r["triggered"][0]["rule"] == "High CPU"

def test_no_alerts():
    rules = [create_rule(name="CPU", metric="cpu_pct", operator="gt", threshold=90)]
    r = evaluate_rules(rules, {"cpu_pct": 50})
    assert r["count"] == 0
    assert r["highest_severity"] is None
