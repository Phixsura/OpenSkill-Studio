from app.services.app_marketplace_app_app_app_app_app_app_app_dns_manager import DnsManager

def test_dns():
    mgr = DnsManager()
    mgr.create_zone("example.com")
    mgr.add_record("example.com", rtype="A", name="@", value="93.184.216.34")
    mgr.add_record("example.com", rtype="CNAME", name="www", value="example.com")
    mgr.add_record("example.com", rtype="TXT", name="@", value="v=spf1 include:_spf.google.com ~all")
    r = mgr.list_records("example.com")
    assert r["count"] == 3
    mgr.remove_record("example.com", name="www", rtype="CNAME")
    assert mgr.list_records("example.com")["count"] == 2

def test_invalid():
    mgr = DnsManager()
    mgr.create_zone("test.com")
    r = mgr.add_record("test.com", rtype="INVALID", name="@", value="x")
    assert "error" in r
