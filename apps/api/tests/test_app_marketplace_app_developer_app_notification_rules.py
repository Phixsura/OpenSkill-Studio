from app.services.app_marketplace_app_developer_app_notification_rules import create_notification_rule, evaluate_rule, get_matching_rules

def test_create():
    r = create_notification_rule(name="Error alert", event_type="error", conditions=[], channels=["email", "slack"])
    assert r["enabled"]

def test_invalid_channel():
    r = create_notification_rule(name="X", event_type="x", conditions=[], channels=["carrier_pigeon"])
    assert r["error"]

def test_evaluate_match():
    rule = {"enabled": True, "event_type": "error", "conditions": [{"field": "severity", "operator": "eq", "value": "critical"}]}
    assert evaluate_rule(rule=rule, event={"type": "error", "data": {"severity": "critical"}})

def test_evaluate_no_match():
    rule = {"enabled": True, "event_type": "error", "conditions": [{"field": "severity", "operator": "eq", "value": "critical"}]}
    assert not evaluate_rule(rule=rule, event={"type": "error", "data": {"severity": "low"}})

def test_matching():
    rules = [
        {"name": "errors", "enabled": True, "event_type": "error", "conditions": []},
        {"name": "installs", "enabled": True, "event_type": "install", "conditions": []},
    ]
    r = get_matching_rules(rules=rules, event={"type": "error", "data": {}})
    assert len(r) == 1
    assert r[0]["name"] == "errors"
