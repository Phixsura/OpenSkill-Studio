from app.services.app_marketplace_extension_response_cache import ResponseCacheService
import time


def test_store_and_lookup():
    rc = ResponseCacheService()
    rc.store("GET", "/api/users", 200, {"users": ["alice"]}, max_age=60)
    result = rc.lookup("GET", "/api/users")
    assert result["hit"] is True
    assert result["status"] == "fresh"
    assert result["body"]["users"] == ["alice"]


def test_miss():
    rc = ResponseCacheService()
    result = rc.lookup("GET", "/api/unknown")
    assert result["hit"] is False


def test_expired():
    rc = ResponseCacheService()
    rc.store("GET", "/api/data", 200, {"x": 1}, max_age=0.01)
    time.sleep(0.02)
    result = rc.lookup("GET", "/api/data")
    assert result["status"] == "expired"


def test_etag_304():
    rc = ResponseCacheService()
    cached = rc.store("GET", "/api/data", 200, {"x": 1}, max_age=60)
    result = rc.lookup("GET", "/api/data", if_none_match=cached.etag)
    assert result["http_status"] == 304
    assert result["status"] == "not_modified"


def test_vary_headers():
    rc = ResponseCacheService()
    rc.store("GET", "/api/page", 200, {"lang": "en"}, max_age=60,
             vary=["Accept-Language"], vary_values={"Accept-Language": "en"})
    rc.store("GET", "/api/page", 200, {"lang": "fr"}, max_age=60,
             vary=["Accept-Language"], vary_values={"Accept-Language": "fr"})
    en = rc.lookup("GET", "/api/page", vary_values={"Accept-Language": "en"})
    fr = rc.lookup("GET", "/api/page", vary_values={"Accept-Language": "fr"})
    assert en["body"]["lang"] == "en"
    assert fr["body"]["lang"] == "fr"


def test_stale_while_revalidate():
    rc = ResponseCacheService()
    rc.store("GET", "/api/data", 200, {"x": 1},
             max_age=0.01, stale_while_revalidate=10)
    time.sleep(0.02)
    result = rc.lookup("GET", "/api/data")
    assert result["status"] == "stale"
    assert result["needs_revalidation"] is True
    assert result["body"]["x"] == 1  # still served


def test_invalidate():
    rc = ResponseCacheService()
    rc.store("GET", "/api/data", 200, {}, max_age=60)
    assert rc.invalidate("GET", "/api/data") is True
    assert rc.lookup("GET", "/api/data")["hit"] is False


def test_purge_expired():
    rc = ResponseCacheService()
    rc.store("GET", "/a", 200, {}, max_age=0.01)
    rc.store("GET", "/b", 200, {}, max_age=60)
    time.sleep(0.02)
    purged = rc.purge_expired()
    assert purged == 1


def test_stats():
    rc = ResponseCacheService()
    rc.store("GET", "/api", 200, {}, max_age=60)
    rc.lookup("GET", "/api")  # hit
    rc.lookup("GET", "/api")  # hit
    rc.lookup("GET", "/other")  # miss
    stats = rc.stats()
    assert stats["hits"] == 2
    assert stats["misses"] == 1
    assert stats["hit_rate"] == 66.7
