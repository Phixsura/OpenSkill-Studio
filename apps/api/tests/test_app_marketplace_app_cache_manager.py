from app.services.app_marketplace_app_cache_manager import AppCacheManager

def test_set_get():
    c = AppCacheManager()
    c.set("k1", {"data": "hello"}, ttl_seconds=3600)
    assert c.get("k1") == {"data": "hello"}

def test_miss():
    c = AppCacheManager()
    assert c.get("missing") is None

def test_invalidate():
    c = AppCacheManager()
    c.set("k1", {"x": 1})
    assert c.invalidate("k1")
    assert c.get("k1") is None

def test_clear():
    c = AppCacheManager()
    c.set("a", {})
    c.set("b", {})
    assert c.clear() == 2
    assert c.stats()["entries"] == 0

def test_stats():
    c = AppCacheManager()
    c.set("k1", {"x": 1})
    c.get("k1")
    c.get("k1")
    s = c.stats()
    assert s["entries"] == 1
    assert s["total_hits"] == 2
