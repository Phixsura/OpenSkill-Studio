from app.services.app_marketplace_app_alerting_rule import create_alert_rule, evaluate_rule

def test_create():
    r = create_alert_rule(name="High Error Rate", metric="error_rate", operator="gt",
                          threshold=5.0, notify=["slack", "email"])
    assert r["rule_id"].startswith("rule_")
    assert r["condition"] == "error_rate > 5.0"

def test_invalid_op():
    r = create_alert_rule(name="X", metric="x", operator="like", threshold=0)
    assert "error" in r

def test_triggered():
    rule = {"rule_id": "r1", "operator": "gt", "threshold": 5.0, "condition": "error_rate > 5.0"}
    r = evaluate_rule(rule=rule, current_value=7.5)
    assert r["triggered"]
    assert r["severity"] == "critical"

def test_not_triggered():
    rule = {"rule_id": "r1", "operator": "gt", "threshold": 5.0, "condition": "error_rate > 5.0"}
    r = evaluate_rule(rule=rule, current_value=2.0)
    assert not r["triggered"]
    assert r["severity"] == "ok"
