from app.services.app_marketplace_app_app_app_app_app_app_app_response_cache import ResponseCache

def test_cache():
    c = ResponseCache(max_size=3, default_ttl=60)
    c.set("k1", {"data": "a"}, now=0)
    r = c.get("k1", now=10)
    assert r["hit"]
    assert r["value"]["data"] == "a"
    r2 = c.get("k1", now=100)
    assert not r2["hit"]  # expired
    s = c.stats()
    assert s["hits"] == 1
    assert s["misses"] == 1

def test_eviction():
    c = ResponseCache(max_size=2)
    c.set("a", {"v": 1}, now=0)
    c.set("b", {"v": 2}, now=0)
    c.set("c", {"v": 3}, now=0)
    assert c.stats()["size"] == 2
    assert not c.get("a", now=0)["hit"]  # evicted
    assert c.get("c", now=0)["hit"]
