from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_meilisearch import fleet_meilisearch_status
def test_ms():
    r = fleet_meilisearch_status([{"healthy": True, "indexes": 10, "documents": 5000000, "search_p50_ms": 10}])
    assert r["documents"] == 5000000
    assert r["fast"]
