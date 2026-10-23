from app.services.app_marketplace_app_app_app_app_app_app_app_token_bucket import TokenBucket

def test_bucket():
    b = TokenBucket(capacity=10, refill_rate=2.0)
    r = b.consume(tokens=5, now=0)
    assert r["allowed"]
    assert r["remaining"] == 5
    r2 = b.consume(tokens=7, now=0)
    assert not r2["allowed"]
    assert r2["retry_after_sec"] == 1.0  # need 2 more tokens, rate=2/s
    # After 3 seconds, refill 6 tokens (capped at 10)
    r3 = b.consume(tokens=7, now=3)
    assert r3["allowed"]
    s = b.status(now=3)
    assert s["tokens"] == 3

def test_status():
    b = TokenBucket(capacity=100, refill_rate=10)
    b.consume(tokens=50, now=0)
    s = b.status(now=0)
    assert s["tokens"] == 50
    assert s["fill_pct"] == 50.0
