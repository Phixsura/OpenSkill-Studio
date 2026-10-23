from app.services.app_marketplace_app_app_app_app_app_app_app_ip_allowlist import validate_ip, check_access, summarize_allowlist

def test_validate():
    assert validate_ip("192.168.1.1")["valid"]
    assert validate_ip("10.0.0.0/8")["valid"]
    assert not validate_ip("not-an-ip")["valid"]

def test_access():
    allow = ["10.0.0.0/8", "192.168.1.0/24"]
    assert check_access(allow, "10.0.0.5")["allowed"]
    assert check_access(allow, "192.168.1.100")["allowed"]
    assert not check_access(allow, "8.8.8.8")["allowed"]
    assert check_access([], "1.2.3.4")["allowed"]  # no restrictions

def test_summary():
    r = summarize_allowlist(["10.0.0.0/8", "bad", "192.168.1.1"])
    assert r["valid"] == 2
    assert r["invalid"] == 1
