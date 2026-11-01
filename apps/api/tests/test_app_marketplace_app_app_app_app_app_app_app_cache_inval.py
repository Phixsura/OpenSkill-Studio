from app.services.app_marketplace_app_app_app_app_app_app_app_cache_inval import CacheInvalidator

def test_set_get():
    c = CacheInvalidator()
    c.set("user:1", '{"name":"alice"}', ["users"])
    r = c.get("user:1")
    assert r["hit"]
    assert r["value"] == '{"name":"alice"}'

def test_invalidate_by_tag():
    c = CacheInvalidator()
    c.set("user:1", "a", ["users"])
    c.set("user:2", "b", ["users"])
    c.set("order:1", "c", ["orders"])
    r = c.invalidate_tag("users")
    assert r["invalidated"] == 2
    assert not c.get("user:1")["hit"]
    assert c.get("order:1")["hit"]

def test_ttl():
    c = CacheInvalidator()
    c.set("k", "v", ["t"], ttl=10)
    assert c.get("k", now=c._cache["k"]["created_at"] + 5)["hit"]
    assert not c.get("k", now=c._cache["k"]["created_at"] + 11)["hit"]
