from app.services.app_marketplace_app_sandbox_networking import validate_egress_rule, build_network_policy

def test_valid_egress():
    r = validate_egress_rule(destination="api.example.com", port=443)
    assert r["valid"]

def test_blocked_port():
    r = validate_egress_rule(destination="db.example.com", port=5432)
    assert not r["valid"]
    assert "blocked" in r["errors"][0]

def test_private_ip():
    r = validate_egress_rule(destination="192.168.1.1", port=443)
    assert not r["valid"]

def test_loopback():
    r = validate_egress_rule(destination="127.0.0.1", port=8080)
    assert not r["valid"]

def test_policy():
    p = build_network_policy(allowed_hosts=["api.example.com"])
    assert not p["allow_private_networks"]
    assert 5432 in p["blocked_ports"]
