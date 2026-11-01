from app.services.app_marketplace_extension_lru_cache import LruCacheWithTtlService
import time


def test_basic_get_put():
    cache = LruCacheWithTtlService(max_entries=10)
    cache.put("key1", "value1")
    assert cache.get("key1") == "value1"
    assert cache.get("missing") is None


def test_lru_eviction():
    cache = LruCacheWithTtlService(max_entries=3)
    cache.put("a", 1)
    cache.put("b", 2)
    cache.put("c", 3)
    # Access 'a' to make it recently used
    cache.get("a")
    # Adding 'd' should evict 'b' (least recently used)
    cache.put("d", 4)
    assert cache.get("b") is None  # evicted
    assert cache.get("a") == 1     # still alive (was accessed)
    assert cache.get("d") == 4


def test_ttl_expiry():
    cache = LruCacheWithTtlService(max_entries=10, default_ttl=0.01)
    cache.put("expire", "soon", ttl=0.01)
    assert cache.get("expire") == "soon"
    time.sleep(0.02)
    assert cache.get("expire") is None


def test_update_existing():
    cache = LruCacheWithTtlService(max_entries=10)
    cache.put("key", "v1", size_bytes=100)
    cache.put("key", "v2", size_bytes=50)
    assert cache.get("key") == "v2"
    assert cache.stats()["size_bytes"] == 50


def test_size_bounded_eviction():
    cache = LruCacheWithTtlService(max_entries=100, max_size_bytes=100)
    cache.put("a", "x", size_bytes=60)
    cache.put("b", "y", size_bytes=60)  # total would be 120 > 100, evict 'a'
    assert cache.get("a") is None
    assert cache.get("b") == "y"


def test_invalidate_prefix():
    cache = LruCacheWithTtlService(max_entries=100)
    cache.put("user:1:profile", "alice")
    cache.put("user:1:settings", "prefs")
    cache.put("user:2:profile", "bob")
    cache.put("post:1", "hello")
    count = cache.invalidate_prefix("user:1:")
    assert count == 2
    assert cache.get("user:1:profile") is None
    assert cache.get("user:2:profile") == "bob"
    assert cache.get("post:1") == "hello"


def test_hit_rate_stats():
    cache = LruCacheWithTtlService(max_entries=10)
    cache.put("a", 1)
    cache.get("a")  # hit
    cache.get("a")  # hit
    cache.get("b")  # miss
    stats = cache.stats()
    assert stats["hits"] == 2
    assert stats["misses"] == 1
    assert stats["hit_rate"] == 66.7


def test_clear():
    cache = LruCacheWithTtlService(max_entries=10)
    cache.put("a", 1, size_bytes=50)
    cache.put("b", 2, size_bytes=30)
    count = cache.clear()
    assert count == 2
    assert cache.stats()["entries"] == 0
    assert cache.stats()["size_bytes"] == 0


def test_delete():
    cache = LruCacheWithTtlService(max_entries=10)
    cache.put("a", 1, size_bytes=100)
    assert cache.delete("a") is True
    assert cache.delete("a") is False
    assert cache.stats()["size_bytes"] == 0


def test_eviction_counter():
    cache = LruCacheWithTtlService(max_entries=2)
    cache.put("a", 1)
    cache.put("b", 2)
    cache.put("c", 3)  # evicts 'a'
    cache.put("d", 4)  # evicts 'b'
    assert cache.stats()["evictions"] == 2
