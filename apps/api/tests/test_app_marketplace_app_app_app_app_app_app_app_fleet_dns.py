from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_dns import fleet_dns_stats
def test_dns():
    r = fleet_dns_stats([{"avg_ms": 10, "failures": 0}, {"avg_ms": 20, "failures": 0}])
    assert r["avg_resolve_ms"] == 15
    assert r["healthy"]
