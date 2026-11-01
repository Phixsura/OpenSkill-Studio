from app.services.app_marketplace_extension_topo_cache import TopoCacheService
import pytest


def test_put_and_get():
    cache = TopoCacheService()
    cache.put("key", "value")
    assert cache.get("key") == "value"


def test_miss():
    cache = TopoCacheService()
    assert cache.get("missing") is None


def test_simple_invalidation():
    cache = TopoCacheService()
    cache.put("key", "value")
    invalidated = cache.invalidate("key")
    assert "key" in invalidated
    assert cache.get("key") is None


def test_cascade_invalidation():
    cache = TopoCacheService()
    cache.put("raw_data", [1, 2, 3])
    cache.put("aggregated", {"sum": 6}, dependencies=["raw_data"])
    cache.put("report", {"title": "Summary"}, dependencies=["aggregated"])
    # Invalidating raw_data should cascade to aggregated and report
    invalidated = cache.invalidate("raw_data")
    assert "raw_data" in invalidated
    assert "aggregated" in invalidated
    assert "report" in invalidated
    assert cache.get("aggregated") is None
    assert cache.get("report") is None


def test_partial_invalidation():
    cache = TopoCacheService()
    cache.put("users", ["alice", "bob"])
    cache.put("user_count", 2, dependencies=["users"])
    cache.put("settings", {"theme": "dark"})  # independent
    cache.invalidate("users")
    assert cache.get("user_count") is None  # invalidated
    assert cache.get("settings") == {"theme": "dark"}  # unaffected


def test_diamond_dependency():
    cache = TopoCacheService()
    cache.put("source", "data")
    cache.put("transform_a", "a", dependencies=["source"])
    cache.put("transform_b", "b", dependencies=["source"])
    cache.put("merged", "ab", dependencies=["transform_a", "transform_b"])
    invalidated = cache.invalidate("source")
    assert set(invalidated) == {"source", "transform_a", "transform_b", "merged"}


def test_cycle_prevention():
    cache = TopoCacheService()
    cache.put("a", 1)
    cache.put("b", 2, dependencies=["a"])
    with pytest.raises(ValueError, match="Circular"):
        cache.put("a", 1, dependencies=["b"])


def test_get_dependents():
    cache = TopoCacheService()
    cache.put("base", 1)
    cache.put("derived_1", 2, dependencies=["base"])
    cache.put("derived_2", 3, dependencies=["base"])
    dependents = cache.get_dependents("base")
    assert set(dependents) == {"derived_1", "derived_2"}


def test_hit_miss_stats():
    cache = TopoCacheService()
    cache.put("x", 1)
    cache.get("x")  # hit
    cache.get("x")  # hit
    cache.get("y")  # miss
    stats = cache.stats()
    assert stats["hits"] == 2
    assert stats["misses"] == 1
    assert stats["hit_rate"] == 66.7


def test_multi_level_cascade():
    cache = TopoCacheService()
    cache.put("l0", "root")
    cache.put("l1", "child", dependencies=["l0"])
    cache.put("l2", "grandchild", dependencies=["l1"])
    cache.put("l3", "great", dependencies=["l2"])
    invalidated = cache.invalidate("l0")
    assert len(invalidated) == 4
