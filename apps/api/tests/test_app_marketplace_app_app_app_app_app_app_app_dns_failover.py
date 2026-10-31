from app.services.app_marketplace_app_app_app_app_app_app_app_dns_failover import DnsFailoverController

def test_failover_failback():
    fc = DnsFailoverController()
    fc.register("api.example.com", "1.1.1.1", "2.2.2.2")
    r = fc.resolve("api.example.com")
    assert r["ip"] == "1.1.1.1"
    fc.failover("api.example.com")
    r2 = fc.resolve("api.example.com")
    assert r2["ip"] == "2.2.2.2"
    fc.failback("api.example.com")
    r3 = fc.resolve("api.example.com")
    assert r3["ip"] == "1.1.1.1"

def test_stats():
    fc = DnsFailoverController()
    fc.register("a.com", "1.1.1.1", "2.2.2.2")
    fc.register("b.com", "3.3.3.3", "4.4.4.4")
    fc.failover("b.com")
    s = fc.status()
    assert s["failed_over"] == 1
