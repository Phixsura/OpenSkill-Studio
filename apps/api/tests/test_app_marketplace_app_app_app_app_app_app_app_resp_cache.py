from app.services.app_marketplace_app_app_app_app_app_app_app_resp_cache import (
    cache_key, get_cached, set_cached, cache_metrics, clear_cache,
)

def test_cache_flow():
    clear_cache()
    key = cache_key("GET", "/api/users")
    assert len(key) == 16
    assert not get_cached(key)["hit"]
    set_cached(key, {"users": [1, 2, 3]}, ttl_sec=300)
    r = get_cached(key)
    assert r["hit"]
    assert r["data"]["users"] == [1, 2, 3]
    assert r["hits"] == 1
    clear_cache()

def test_metrics():
    clear_cache()
    k1 = cache_key("GET", "/a")
    set_cached(k1, {"a": 1})
    get_cached(k1)
    get_cached(k1)
    m = cache_metrics()
    assert m["total_keys"] == 1
    assert m["total_hits"] == 2
    clear_cache()
