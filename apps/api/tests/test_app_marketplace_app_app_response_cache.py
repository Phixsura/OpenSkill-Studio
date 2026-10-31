from app.services.app_marketplace_app_app_response_cache import build_cache_headers, generate_etag, check_conditional

def test_public_cache():
    r = build_cache_headers(max_age_s=3600, public=True)
    assert "public" in r["Cache-Control"]
    assert "max-age=3600" in r["Cache-Control"]
    assert r["cacheable"]

def test_no_store():
    r = build_cache_headers(no_store=True)
    assert "no-store" in r["Cache-Control"]
    assert not r["cacheable"]

def test_stale_revalidate():
    r = build_cache_headers(stale_while_revalidate_s=60)
    assert "stale-while-revalidate=60" in r["Cache-Control"]

def test_etag():
    r = generate_etag(content="hello world")
    assert r["etag_weak"].startswith('W/"')
    assert len(r["hash"]) == 16

def test_conditional_hit():
    etag = generate_etag(content="test")
    r = check_conditional(etag=etag["etag_strong"], if_none_match=etag["etag_strong"])
    assert r["status"] == 304
    assert r["cache_hit"]

def test_conditional_miss():
    r = check_conditional(etag='"abc"', if_none_match='"xyz"')
    assert r["status"] == 200
