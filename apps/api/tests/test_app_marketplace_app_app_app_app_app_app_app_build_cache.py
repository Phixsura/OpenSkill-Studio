from app.services.app_marketplace_app_app_app_app_app_app_app_build_cache import (
    cache_build, lookup_cache, cache_efficiency, clear_build_cache,
)

def test_cache():
    clear_build_cache()
    cache_build("api:v2.0", ["base", "deps", "app"], 250.0)
    r = lookup_cache("api:v2.0")
    assert r["hit"]
    assert r["layers"] == 3
    lookup_cache("api:v2.0")
    e = cache_efficiency()
    assert e["total_hits"] == 2
    assert e["total_size_mb"] == 250.0
    clear_build_cache()

def test_miss():
    clear_build_cache()
    assert not lookup_cache("missing")["hit"]
    clear_build_cache()
