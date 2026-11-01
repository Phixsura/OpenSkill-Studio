from app.services.app_marketplace_app_cache_manager import get_cache_stats, invalidate_cache

def test_stats():
    caches = [
        {"name": "L1", "type": "memory", "hits": 900, "misses": 100, "size_mb": 64, "max_size_mb": 128},
        {"name": "L2", "type": "redis", "hits": 800, "misses": 200, "size_mb": 256, "max_size_mb": 512},
    ]
    r = get_cache_stats(caches=caches)
    assert r["overall_hit_rate"] == 85.0
    assert r["caches"][0]["hit_rate"] == 90.0

def test_invalidate():
    r = invalidate_cache(cache_name="L1", pattern="/api/apps/*")
    assert r["status"] == "invalidated"
    assert r["keys_affected"] == "partial"

def test_invalidate_all():
    r = invalidate_cache(cache_name="L1")
    assert r["keys_affected"] == "all"
