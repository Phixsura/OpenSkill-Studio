from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_dns_security_v9 import fleet_dns_security_v9
def test_dnssec_v9():
    r = fleet_dns_security_v9([{"dnssec_enabled": True, "doh_enabled": True, "blocked_queries": 100}])
    assert r["dnssec_enabled"] == 1
    assert r["healthy"]
