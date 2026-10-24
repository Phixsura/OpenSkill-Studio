from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_dns_resolver_v9 import fleet_dns_resolver_v9
def test_dns_v9():
    r = fleet_dns_resolver_v9([{"active": True, "queries_per_sec": 5000, "ttl": 60}, {"active": True, "queries_per_sec": 3000, "ttl": 120}])
    assert r["qps"] == 8000
    assert r["healthy"]
