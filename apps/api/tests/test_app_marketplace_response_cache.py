from app.services.app_marketplace_response_cache import ResponseCache


def test_put_and_get():
    rc = ResponseCache()
    rc.put("key1", b'{"data": []}', max_age=300)
    entry, status = rc.get("key1")
    assert status == "hit"
    assert entry.body == b'{"data": []}'


def test_miss():
    rc = ResponseCache()
    entry, status = rc.get("nonexistent")
    assert status == "miss"
    assert entry is None


def test_etag_not_modified():
    rc = ResponseCache()
    cached = rc.put("key2", b"hello")
    entry, status = rc.get("key2", if_none_match=cached.etag)
    assert status == "not_modified"


def test_expired():
    rc = ResponseCache()
    rc.put("key3", b"old", max_age=0)  # immediate expiry
    entry, status = rc.get("key3")
    assert status == "miss"


def test_stale_while_revalidate():
    rc = ResponseCache()
    rc.put("key4", b"data", max_age=0, stale_while_revalidate=3600)
    entry, status = rc.get("key4")
    assert status == "stale"
    assert entry is not None


def test_invalidate_by_tag():
    rc = ResponseCache()
    rc.put("a", b"1", tags=["ext-1"])
    rc.put("b", b"2", tags=["ext-1", "config"])
    rc.put("c", b"3", tags=["ext-2"])
    removed = rc.invalidate_by_tag("ext-1")
    assert removed == 2
    assert rc.get("c")[1] == "hit"


def test_cache_headers():
    rc = ResponseCache()
    entry = rc.put("h1", b"body", max_age=600, stale_while_revalidate=60)
    headers = rc.get_cache_headers(entry)
    assert "ETag" in headers
    assert "max-age=600" in headers["Cache-Control"]
    assert "stale-while-revalidate=60" in headers["Cache-Control"]


def test_stats():
    rc = ResponseCache()
    rc.put("s1", b"a", max_age=3600)
    rc.put("s2", b"b", max_age=3600)
    s = rc.stats()
    assert s["total"] == 2
    assert s["fresh"] == 2
