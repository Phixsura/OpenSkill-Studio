from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_dns import fleet_ai_dns_resolver
def test_dns():
    r = fleet_ai_dns_resolver([{"active": True, "queries_24h": 100000000, "cache_hit_pct": 95, "services": 500}])
    assert r["cache_hit_pct"] == 95.0
    assert r["fast"]
