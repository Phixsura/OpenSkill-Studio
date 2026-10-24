from app.services.app_marketplace_app_app_ip_allowlist import validate_cidr, check_ip, build_allowlist

def test_valid_cidr():
    r = validate_cidr(cidr="10.0.0.0/24")
    assert r["valid"]
    assert r["num_hosts"] == 256

def test_single_ip():
    r = validate_cidr(cidr="192.168.1.1/32")
    assert r["is_single"]

def test_invalid():
    r = validate_cidr(cidr="not-a-cidr")
    assert not r["valid"]

def test_check_allowed():
    r = check_ip(ip="10.0.0.5", allowlist=["10.0.0.0/24"])
    assert r["allowed"]

def test_check_denied():
    r = check_ip(ip="192.168.1.1", allowlist=["10.0.0.0/24"])
    assert not r["allowed"]

def test_allowlist():
    rules = [{"cidr": "10.0.0.0/8", "label": "Internal"}, {"cidr": "bad", "label": "Broken"}]
    r = build_allowlist(rules=rules)
    assert r["total"] == 2
    assert r["valid_count"] == 1
