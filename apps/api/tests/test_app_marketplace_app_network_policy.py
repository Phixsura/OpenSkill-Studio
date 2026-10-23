from app.services.app_marketplace_app_network_policy import create_network_policy

def test_valid():
    rules = [
        {"direction": "egress", "target": "api.stripe.com", "port": 443, "protocol": "tcp"},
        {"direction": "egress", "target": "*", "port": 53, "protocol": "udp", "action": "allow"},
    ]
    r = create_network_policy(app_id="a1", rules=rules)
    assert r["valid"]
    assert r["egress_count"] == 2

def test_invalid_target():
    rules = [{"direction": "egress", "target": "not valid!"}]
    r = create_network_policy(app_id="a1", rules=rules)
    assert not r["valid"]

def test_invalid_direction():
    rules = [{"direction": "sideways", "target": "api.example.com"}]
    r = create_network_policy(app_id="a1", rules=rules)
    assert not r["valid"]
