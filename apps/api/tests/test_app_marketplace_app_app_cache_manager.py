from app.services.app_marketplace_app_app_cache_manager import CacheManager

def test_set_get():
    c = CacheManager(max_size=5, ttl_s=10)
    c.set("k1", "v1", now=0)
    assert c.get("k1", now=1) == "v1"
    assert c.hits == 1

def test_miss():
    c = CacheManager()
    assert c.get("missing") is None
    assert c.misses == 1

def test_ttl_expiry():
    c = CacheManager(max_size=100, ttl_s=5)
    c.set("k", "v", now=0)
    assert c.get("k", now=6) is None

def test_lru_eviction():
    c = CacheManager(max_size=2, ttl_s=100)
    c.set("a", 1, now=0)
    c.set("b", 2, now=0)
    c.set("c", 3, now=0)  # evicts "a"
    assert c.get("a", now=0) is None
    assert c.get("b", now=0) == 2

def test_stats():
    c = CacheManager()
    c.set("k", "v", now=0)
    c.get("k", now=1)
    c.get("miss", now=1)
    s = c.stats()
    assert s["hits"] == 1
    assert s["misses"] == 1
    assert s["hit_rate"] == 50.0
