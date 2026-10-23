from app.services.app_marketplace_app_response_cache import compute_cache_key, build_cache_headers, should_cache, compute_cache_hit_rate

def test_cache_key():
    k1 = compute_cache_key(method="GET", path="/users")
    k2 = compute_cache_key(method="GET", path="/users", query_params={"limit": "10"})
    assert k1 != k2
    assert len(k1) == 16

def test_deterministic():
    k1 = compute_cache_key(method="GET", path="/x")
    k2 = compute_cache_key(method="GET", path="/x")
    assert k1 == k2

def test_headers():
    h = build_cache_headers(max_age=600, private=True)
    assert "private" in h["Cache-Control"]
    assert "max-age=600" in h["Cache-Control"]

def test_should_cache_get():
    assert should_cache(method="GET", status_code=200, content_type="application/json")

def test_should_not_cache_post():
    assert not should_cache(method="POST", status_code=200, content_type="application/json")

def test_should_not_cache_500():
    assert not should_cache(method="GET", status_code=500, content_type="application/json")

def test_hit_rate():
    r = compute_cache_hit_rate(hits=900, misses=100)
    assert r["hit_rate"] == 90.0
    assert r["efficiency"] == "good"
