from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_cache_ratio import fleet_cache_ratio
def test_ratio():
    r = fleet_cache_ratio([{"hits": 900, "misses": 100}, {"hits": 800, "misses": 200}])
    assert r["hits"] == 1700
    assert r["ratio_pct"] == 85.0
    assert r["effective"]
