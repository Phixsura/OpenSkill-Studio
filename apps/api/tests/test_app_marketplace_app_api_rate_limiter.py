from app.services.app_marketplace_app_api_rate_limiter import create_bucket, try_consume, get_rate_limit_headers

def test_create():
    b = create_bucket(capacity=100, refill_rate=10)
    assert b["tokens"] == 100
    assert b["capacity"] == 100

def test_consume_ok():
    b = create_bucket(capacity=100, refill_rate=10, tokens=50)
    r = try_consume(bucket=b, tokens=5)
    assert r["allowed"]
    assert r["remaining"] >= 45

def test_consume_denied():
    b = create_bucket(capacity=100, refill_rate=10, tokens=0)
    # tokens=0 and no time elapsed → denied
    r = try_consume(bucket=b, tokens=5)
    assert not r["allowed"]
    assert r["retry_after_sec"] > 0

def test_headers():
    result = {"capacity": 100, "remaining": 50, "retry_after_sec": 0}
    h = get_rate_limit_headers(result=result)
    assert h["X-RateLimit-Limit"] == "100"
    assert h["X-RateLimit-Remaining"] == "50"
