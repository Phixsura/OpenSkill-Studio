from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_coredns import fleet_coredns_status
def test_dns():
    r = fleet_coredns_status([{"healthy": True, "qps": 10000, "cache_hit_pct": 85}])
    assert r["qps"] == 10000
    assert r["cache_hit_pct"] == 85.0
    assert r["all_healthy"]
