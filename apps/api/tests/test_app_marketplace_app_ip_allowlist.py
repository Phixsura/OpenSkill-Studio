from app.services.app_marketplace_app_ip_allowlist import validate_ip_entry, check_ip_allowed, get_allowlist_summary

def test_validate_ip():
    r = validate_ip_entry(entry="192.168.1.0/24")
    assert r["valid"]
    assert r["num_addresses"] == 256

def test_validate_invalid():
    r = validate_ip_entry(entry="not-an-ip")
    assert not r["valid"]

def test_allowed():
    r = check_ip_allowed(client_ip="10.0.0.5", allowlist=["10.0.0.0/8"])
    assert r["allowed"]

def test_blocked():
    r = check_ip_allowed(client_ip="192.168.1.1", allowlist=["10.0.0.0/8"])
    assert not r["allowed"]

def test_empty_list():
    r = check_ip_allowed(client_ip="1.2.3.4", allowlist=[])
    assert r["allowed"]

def test_summary():
    r = get_allowlist_summary(entries=["10.0.0.0/8", "bad", "192.168.0.0/16"])
    assert r["valid_rules"] == 2
    assert r["invalid_rules"] == 1
