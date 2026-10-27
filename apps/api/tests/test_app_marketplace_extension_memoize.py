from app.services.app_marketplace_extension_memoize import MemoizeCacheService
import time


def test_basic_memoization():
    mc = MemoizeCacheService()
    mc.register("add")
    call_count = [0]
    def add(a, b):
        call_count[0] += 1
        return a + b
    assert mc.get_or_compute("add", add, (2, 3)) == 5
    assert mc.get_or_compute("add", add, (2, 3)) == 5  # cached
    assert call_count[0] == 1  # only computed once


def test_different_args():
    mc = MemoizeCacheService()
    mc.register("square")
    def square(n): return n * n
    mc.get_or_compute("square", square, (3,))
    mc.get_or_compute("square", square, (4,))
    mc.get_or_compute("square", square, (3,))  # hit
    stats = mc.get_stats("square")
    assert stats["hits"] == 1
    assert stats["misses"] == 2


def test_ttl_expiry():
    mc = MemoizeCacheService()
    mc.register("fn", ttl_seconds=0.01)
    def fn(): return "result"
    mc.get_or_compute("fn", fn)
    time.sleep(0.02)
    # Should recompute after TTL
    call_count = [0]
    def fn2():
        call_count[0] += 1
        return "new"
    mc.get_or_compute("fn", fn2)
    assert call_count[0] == 1  # recomputed


def test_lru_eviction():
    mc = MemoizeCacheService()
    mc.register("fn", max_size=3)
    def fn(x): return x * 2
    mc.get_or_compute("fn", fn, (1,))
    mc.get_or_compute("fn", fn, (2,))
    mc.get_or_compute("fn", fn, (3,))
    mc.get_or_compute("fn", fn, (4,))  # evicts (1,)
    stats = mc.get_stats("fn")
    assert stats["evictions"] == 1
    assert stats["cached_entries"] == 3


def test_lru_access_refreshes():
    mc = MemoizeCacheService()
    mc.register("fn", max_size=3)
    def fn(x): return x
    mc.get_or_compute("fn", fn, (1,))
    mc.get_or_compute("fn", fn, (2,))
    mc.get_or_compute("fn", fn, (3,))
    mc.get_or_compute("fn", fn, (1,))  # refresh (1)
    mc.get_or_compute("fn", fn, (4,))  # should evict (2), not (1)
    # (1) should still be cached
    call_count = [0]
    def fn2(x):
        call_count[0] += 1
        return x
    mc.get_or_compute("fn", fn2, (1,))
    assert call_count[0] == 0  # hit, not recomputed


def test_invalidate_specific():
    mc = MemoizeCacheService()
    mc.register("fn")
    def fn(x): return x
    mc.get_or_compute("fn", fn, (1,))
    mc.get_or_compute("fn", fn, (2,))
    mc.invalidate("fn", (1,))
    assert mc.get_stats("fn")["cached_entries"] == 1


def test_invalidate_all():
    mc = MemoizeCacheService()
    mc.register("fn")
    def fn(x): return x
    for i in range(10):
        mc.get_or_compute("fn", fn, (i,))
    cleared = mc.invalidate_all("fn")
    assert cleared == 10
    assert mc.get_stats("fn")["cached_entries"] == 0


def test_kwargs():
    mc = MemoizeCacheService()
    mc.register("fn")
    def greet(name, greeting="hello"):
        return f"{greeting} {name}"
    mc.get_or_compute("fn", greet, ("Alice",), {"greeting": "hi"})
    mc.get_or_compute("fn", greet, ("Alice",), {"greeting": "hi"})  # hit
    mc.get_or_compute("fn", greet, ("Alice",), {"greeting": "bye"})  # miss
    assert mc.get_stats("fn")["hits"] == 1
    assert mc.get_stats("fn")["misses"] == 2


def test_hit_rate():
    mc = MemoizeCacheService()
    mc.register("fn")
    def fn(x): return x
    mc.get_or_compute("fn", fn, (1,))  # miss
    mc.get_or_compute("fn", fn, (1,))  # hit
    mc.get_or_compute("fn", fn, (1,))  # hit
    mc.get_or_compute("fn", fn, (2,))  # miss
    stats = mc.get_stats("fn")
    assert stats["hit_rate"] == 50.0
