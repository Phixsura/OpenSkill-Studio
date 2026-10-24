from app.services.app_marketplace_app_app_notification_rule import create_notification_rule, evaluate_rules

def test_create():
    r = create_notification_rule(name="High Error Rate", rule_type="threshold",
        condition={"metric": "error_rate", "operator": "gt", "threshold": 5},
        channels=["email", "slack"])
    assert r["name"] == "High Error Rate"
    assert r["channels"] == ["email", "slack"]

def test_invalid_channel():
    r = create_notification_rule(name="X", rule_type="threshold",
        condition={}, channels=["carrier_pigeon"])
    assert "error" in r

def test_evaluate():
    rules = [
        {"name": "High Errors", "enabled": True,
         "condition": {"metric": "error_rate", "operator": "gt", "threshold": 5}},
        {"name": "Low Uptime", "enabled": True,
         "condition": {"metric": "uptime", "operator": "lt", "threshold": 99}},
    ]
    r = evaluate_rules(rules=rules, metrics={"error_rate": 8, "uptime": 99.5})
    assert r["triggered_count"] == 1
    assert r["triggered"][0]["rule"] == "High Errors"
