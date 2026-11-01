from app.services.app_marketplace_app_app_app_app_app_app_app_token_bucket import TokenBucket

def test_consume():
    tb = TokenBucket(capacity=10, refill_rate=1.0)
    r = tb.consume("u1", 3, now=0)
    assert r["allowed"]
    assert r["remaining"] == 7

def test_exhausted():
    tb = TokenBucket(capacity=2, refill_rate=0.5)
    tb.consume("u1", 2, now=0)
    r = tb.consume("u1", 1, now=0)
    assert not r["allowed"]
    assert r["retry_after_seconds"] == 2.0

def test_refill():
    tb = TokenBucket(capacity=5, refill_rate=1.0)
    tb.consume("u1", 5, now=0)
    r = tb.peek("u1", now=3)
    assert r["tokens"] == 3
