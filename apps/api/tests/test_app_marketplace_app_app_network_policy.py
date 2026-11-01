from app.services.app_marketplace_app_app_network_policy import build_network_policy

def test_basic():
    rules = [
        {"direction": "ingress", "protocol": "tcp", "port": 443, "action": "allow", "source": "0.0.0.0/0"},
        {"direction": "ingress", "protocol": "tcp", "port": 80, "action": "allow"},
        {"direction": "egress", "protocol": "tcp", "port": 5432, "source": "10.0.0.0/8", "description": "Database"},
    ]
    r = build_network_policy(rules=rules)
    assert r["valid"]
    assert r["ingress_count"] == 2
    assert r["egress_count"] == 1

def test_invalid_port():
    r = build_network_policy(rules=[{"port": 99999, "protocol": "tcp"}])
    assert not r["valid"]

def test_invalid_protocol():
    r = build_network_policy(rules=[{"protocol": "ftp"}])
    assert not r["valid"]
