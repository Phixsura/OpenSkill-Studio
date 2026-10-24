from app.services.app_marketplace_app_app_app_app_app_app_app_dedup_cache import DedupCache

def test_cache():
    dc = DedupCache(ttl_seconds=60)
    dc.store("POST", "/api/orders", "abc", {"order_id": "o1"})
    r = dc.check("POST", "/api/orders", "abc")
    assert r["hit"]
    assert r["response"]["order_id"] == "o1"
    r2 = dc.check("POST", "/api/orders", "xyz")
    assert not r2["hit"]
    assert dc.stats()["hit_rate"] == 50.0

def test_expired():
    import time
    dc = DedupCache(ttl_seconds=1)
    dc.store("GET", "/a", "h1", {"ok": True})
    r = dc.check("GET", "/a", "h1", now=time.time() + 2)
    assert not r["hit"]
