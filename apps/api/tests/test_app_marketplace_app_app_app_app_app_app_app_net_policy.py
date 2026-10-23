from app.services.app_marketplace_app_app_app_app_app_app_app_net_policy import create_rule, evaluate_traffic

def test_create():
    r = create_rule("block-external", "egress", "deny", "*", "0.0.0.0/0", 0)
    assert r["created"]

def test_evaluate():
    rules = [
        create_rule("allow-http", "ingress", "allow", "*", "10.0.0.1", 80),
        create_rule("deny-ssh", "ingress", "deny", "*", "*", 22),
    ]
    r = evaluate_traffic(rules, "ingress", "1.2.3.4", "10.0.0.1", 80)
    assert r["allowed"]
    r2 = evaluate_traffic(rules, "ingress", "1.2.3.4", "10.0.0.1", 22)
    assert not r2["allowed"]
    assert r2["matched_rule"] == "deny-ssh"
