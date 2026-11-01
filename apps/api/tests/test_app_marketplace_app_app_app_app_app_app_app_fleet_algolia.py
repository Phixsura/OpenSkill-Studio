from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_algolia import fleet_algolia_status
def test_alg():
    r = fleet_algolia_status([{"records": 10000000, "operations_24h": 50000000, "avg_latency_ms": 5}])
    assert r["records"] == 10000000
    assert r["fast"]
