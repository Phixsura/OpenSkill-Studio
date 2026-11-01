from app.services.app_marketplace_cache_service import CacheService


def test_set_and_get():
    cache = CacheService()
    cache.set("key1", {"name": "Test"})
    assert cache.get("key1") == {"name": "Test"}


def test_miss():
    cache = CacheService()
    assert cache.get("nonexistent") is None


def test_ttl_expiry():
    cache = CacheService()
    cache.set("fast", "val", ttl=0.0)  # expires immediately
    assert cache.get("fast") is None


def test_delete():
    cache = CacheService()
    cache.set("del", "val")
    assert cache.delete("del") is True
    assert cache.get("del") is None


def test_has():
    cache = CacheService()
    cache.set("exists", 1)
    assert cache.has("exists") is True
    assert cache.has("nope") is False


def test_get_or_set():
    cache = CacheService()
    calls = []
    def factory():
        calls.append(1)
        return "computed"
    assert cache.get_or_set("lazy", factory) == "computed"
    assert cache.get_or_set("lazy", factory) == "computed"
    assert len(calls) == 1  # factory only called once


def test_invalidate_prefix():
    cache = CacheService()
    cache.set("ext:1:config", "a")
    cache.set("ext:1:data", "b")
    cache.set("ext:2:config", "c")
    removed = cache.invalidate_prefix("ext:1:")
    assert removed == 2
    assert cache.has("ext:2:config") is True


def test_stats():
    cache = CacheService()
    cache.set("a", 1)
    cache.get("a")
    cache.get("a")
    cache.get("miss")
    s = cache.stats()
    assert s["hits"] == 2
    assert s["misses"] == 1
    assert s["hit_rate"] > 0.6


def test_eviction():
    cache = CacheService(max_entries=3)
    cache.set("a", 1)
    cache.set("b", 2)
    cache.set("c", 3)
    cache.get("a")  # boost a's hits
    cache.get("a")
    cache.set("d", 4)  # should evict b or c (lowest hits)
    assert cache.has("a") is True  # kept (most hits)
    assert cache.has("d") is True  # just added
