from app.services.app_rate_limit_response import build_rate_limit_response

def test_under_limit():
    r = build_rate_limit_response(limit=1000, remaining=500, reset_seconds=60)
    assert r["exceeded"] is False
    assert r["error_body"] is None
    assert r["headers"]["X-RateLimit-Remaining"] == "500"

def test_at_limit():
    r = build_rate_limit_response(limit=1000, remaining=0, reset_seconds=30)
    assert r["exceeded"] is True
    assert r["error_body"] is not None
    assert r["headers"]["Retry-After"] == "30"

def test_headers_present():
    r = build_rate_limit_response(limit=100, remaining=50, reset_seconds=60)
    assert "X-RateLimit-Limit" in r["headers"]
    assert "X-RateLimit-Reset" in r["headers"]
