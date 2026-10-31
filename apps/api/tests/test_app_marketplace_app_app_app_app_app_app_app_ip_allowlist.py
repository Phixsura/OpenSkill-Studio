from app.services.app_marketplace_app_app_app_app_app_app_app_ip_allowlist import IpAllowlist

def test_allow():
    al = IpAllowlist()
    al.add_rule("office", "10.0.0.0/8", "Office network")
    al.add_rule("vpn", "192.168.1.0/24", "VPN")
    r = al.check("10.1.2.3")
    assert r["allowed"]
    assert r["matched_rule"] == "office"

def test_deny():
    al = IpAllowlist()
    al.add_rule("office", "10.0.0.0/8")
    r = al.check("8.8.8.8")
    assert not r["allowed"]

def test_remove():
    al = IpAllowlist()
    al.add_rule("test", "1.2.3.0/24")
    al.remove_rule("test")
    assert len(al.list_rules()) == 0

def test_invalid_ip():
    al = IpAllowlist()
    r = al.check("not-an-ip")
    assert not r["allowed"]
