from app.services.app_marketplace_app_app_app_app_app_app_app_firewall_rules import (
    create_rule, evaluate_rules, firewall_summary,
)

def test_create():
    r = create_rule("allow-http", "ingress", "allow", "tcp", 80, "10.0.0.0/8")
    assert r["created"]
    r2 = create_rule("bad", "ingress", "allow", "tcp", 80, "invalid")
    assert not r2["created"]

def test_evaluate():
    rules = [
        {"name": "allow-http", "direction": "ingress", "action": "allow", "port": 80, "source": "0.0.0.0/0", "priority": 100},
        {"name": "deny-ssh", "direction": "ingress", "action": "deny", "port": 22, "source": "0.0.0.0/0", "priority": 50},
    ]
    r = evaluate_rules(rules, "ingress", 80, "1.2.3.4")
    assert r["action"] == "allow"
    r2 = evaluate_rules(rules, "ingress", 22, "1.2.3.4")
    assert r2["action"] == "deny"

def test_summary():
    rules = [
        {"action": "allow", "direction": "ingress"},
        {"action": "deny", "direction": "ingress"},
        {"action": "allow", "direction": "egress"},
    ]
    r = firewall_summary(rules)
    assert r["allow"] == 2
    assert r["deny"] == 1
