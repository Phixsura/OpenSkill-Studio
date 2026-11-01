from app.services.app_marketplace_extension_api_response_cache import (
    ApiResponseCacheService,
)


def test_set_and_get():
    svc = ApiResponseCacheService()
    svc.set("GET", "/api/users", '{"users": []}')
    result = svc.get("GET", "/api/users")
    assert result == '{"users": []}'


def test_cache_miss():
    svc = ApiResponseCacheService()
    assert svc.get("GET", "/unknown") is None


def test_ttl_expiry():
    svc = ApiResponseCacheService()
    svc.set("GET", "/api/data", "old", ttl_seconds=-1)
    assert svc.get("GET", "/api/data") is None


def test_invalidate():
    svc = ApiResponseCacheService()
    svc.set("GET", "/api/users", "data")
    assert svc.invalidate("GET", "/api/users") is True
    assert svc.get("GET", "/api/users") is None


def test_lru_eviction():
    svc = ApiResponseCacheService(max_entries=2)
    svc.set("GET", "/a", "1")
    svc.set("GET", "/b", "2")
    svc.set("GET", "/c", "3")  # should evict /a
    assert svc.get("GET", "/a") is None
    assert svc.get("GET", "/c") == "3"


def test_hit_rate():
    svc = ApiResponseCacheService()
    svc.set("GET", "/api", "data")
    svc.get("GET", "/api")  # hit
    svc.get("GET", "/api")  # hit
    svc.get("GET", "/miss")  # miss
    stats = svc.get_stats()
    assert stats["hits"] == 2
    assert stats["misses"] == 1
    assert stats["hit_rate"] == 66.7


def test_params_differentiation():
    svc = ApiResponseCacheService()
    svc.set("GET", "/api/search", "page1", params="page=1")
    svc.set("GET", "/api/search", "page2", params="page=2")
    assert svc.get("GET", "/api/search", "page=1") == "page1"
    assert svc.get("GET", "/api/search", "page=2") == "page2"


def test_clear():
    svc = ApiResponseCacheService()
    svc.set("GET", "/a", "1")
    svc.set("GET", "/b", "2")
    assert svc.clear() == 2
    assert svc.get_stats()["entries"] == 0
