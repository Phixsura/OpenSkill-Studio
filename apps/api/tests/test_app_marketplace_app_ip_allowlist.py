from app.services.app_marketplace_app_ip_allowlist import validate_ip_entry, check_ip_allowed, build_allowlist_summary

def test_valid_ip():
    r = validate_ip_entry("192.168.1.1")
    assert r["valid"]
    assert r["type"] == "single"

def test_valid_cidr():
    r = validate_ip_entry("10.0.0.0/24")
    assert r["valid"]
    assert r["addresses"] == 256

def test_invalid():
    r = validate_ip_entry("not-an-ip")
    assert not r["valid"]

def test_allowed():
    assert check_ip_allowed(ip="10.0.0.5", allowlist=["10.0.0.0/24"])

def test_denied():
    assert not check_ip_allowed(ip="192.168.1.1", allowlist=["10.0.0.0/24"])

def test_empty_allows_all():
    assert check_ip_allowed(ip="1.2.3.4", allowlist=[])

def test_summary():
    s = build_allowlist_summary(entries=["10.0.0.0/24", "192.168.1.1", "bad"])
    assert s["valid_entries"] == 2
    assert len(s["invalid_entries"]) == 1
