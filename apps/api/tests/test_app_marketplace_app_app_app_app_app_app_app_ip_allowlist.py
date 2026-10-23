from app.services.app_marketplace_app_app_app_app_app_app_app_ip_allowlist import IpAllowlistManager

def test_allowlist():
    mgr = IpAllowlistManager()
    mgr.add_rule(cidr="10.0.0.0/8", label="Internal")
    mgr.add_rule(cidr="203.0.113.0/24", label="Office")
    r = mgr.check_ip("10.1.2.3")
    assert r["allowed"]
    assert r["label"] == "Internal"
    r2 = mgr.check_ip("8.8.8.8")
    assert not r2["allowed"]
    assert r2["reason"] == "not_in_allowlist"

def test_invalid():
    mgr = IpAllowlistManager()
    r = mgr.add_rule(cidr="not-a-cidr")
    assert "error" in r

def test_remove():
    mgr = IpAllowlistManager()
    mgr.add_rule(cidr="10.0.0.0/8", label="Internal")
    assert len(mgr.list_rules()) == 1
    mgr.remove_rule("10.0.0.0/8")
    assert len(mgr.list_rules()) == 0
