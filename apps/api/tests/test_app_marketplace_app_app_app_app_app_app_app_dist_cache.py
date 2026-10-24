from app.services.app_marketplace_app_app_app_app_app_app_app_dist_cache import DistributedCache

def test_set_get():
    dc = DistributedCache(shards=4)
    dc.set("user:1", '{"name":"alice"}')
    r = dc.get("user:1")
    assert r["hit"]
    assert r["value"] == '{"name":"alice"}'

def test_miss():
    dc = DistributedCache()
    r = dc.get("missing")
    assert not r["hit"]
    assert dc.stats()["misses"] == 1

def test_delete():
    dc = DistributedCache()
    dc.set("k", "v")
    dc.delete("k")
    assert not dc.get("k")["hit"]

def test_stats():
    dc = DistributedCache(shards=2)
    for i in range(10):
        dc.set(f"key-{i}", f"val-{i}")
    s = dc.stats()
    assert s["total_keys"] == 10
    assert s["shards"] == 2
