from app.services.app_marketplace_app_app_app_app_app_app_app_cache_mgr import (
    cache_set, cache_get, cache_stats, cache_clear,
)

def test_set_get():
    cache_clear()
    cache_set("k1", {"data": 42}, ttl_sec=3600)
    r = cache_get("k1")
    assert r["hit"]
    assert r["value"]["data"] == 42
    assert r["hits"] == 1

def test_miss():
    cache_clear()
    r = cache_get("missing")
    assert not r["hit"]

def test_stats():
    cache_clear()
    cache_set("a", 1)
    cache_set("b", 2)
    cache_get("a")
    cache_get("a")
    s = cache_stats()
    assert s["total_keys"] == 2
    assert s["total_hits"] == 2
    cache_clear()
