from app.services.app_marketplace_app_response_cache import generate_etag, build_cache_headers, check_conditional

def test_etag():
    e1 = generate_etag(content="hello")
    e2 = generate_etag(content="hello")
    e3 = generate_etag(content="world")
    assert e1 == e2
    assert e1 != e3
    assert e1.startswith('"') and e1.endswith('"')

def test_headers():
    r = build_cache_headers(content="test", max_age=600, private=True)
    assert "private" in r["Cache-Control"]
    assert "max-age=600" in r["Cache-Control"]
    assert r["Vary"] == "Accept-Encoding"

def test_conditional_match():
    etag = generate_etag(content="data")
    r = check_conditional(if_none_match=etag, current_etag=etag)
    assert r["status"] == 304
    assert not r["send_body"]

def test_conditional_miss():
    r = check_conditional(if_none_match='"old"', current_etag='"new"')
    assert r["status"] == 200
    assert r["send_body"]
