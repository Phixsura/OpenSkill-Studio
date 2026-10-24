from app.services.app_marketplace_app_app_app_app_app_app_app_resp_cache import ResponseCache

def test_cache_hit():
    rc = ResponseCache(default_ttl=60)
    rc.set("GET:/users", '{"users":[]}')
    r = rc.get("GET:/users")
    assert r["hit"]
    assert r["body"] == '{"users":[]}'

def test_etag():
    rc = ResponseCache()
    stored = rc.set("k", "data")
    r = rc.get("k", etag=stored["etag"])
    assert r["not_modified"]

def test_miss():
    rc = ResponseCache()
    r = rc.get("missing")
    assert not r["hit"]
    assert rc.stats()["misses"] == 1
