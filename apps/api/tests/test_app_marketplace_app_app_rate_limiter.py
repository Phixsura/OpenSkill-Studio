from app.services.app_marketplace_app_app_rate_limiter import TokenBucket, hash_client_key

def test_allow():
    b = TokenBucket(capacity=10, refill_rate=1.0)
    r = b.consume("user1", tokens=1, now=0)
    assert r["allowed"]
    assert r["remaining"] == 9

def test_deny():
    b = TokenBucket(capacity=2, refill_rate=0.5)
    b.consume("u", tokens=2, now=0)
    r = b.consume("u", tokens=1, now=0)
    assert not r["allowed"]
    assert r["retry_after_s"] == 2.0

def test_refill():
    b = TokenBucket(capacity=5, refill_rate=1.0)
    b.consume("u", tokens=5, now=0)
    r = b.consume("u", tokens=1, now=3)
    assert r["allowed"]
    assert r["remaining"] == 2

def test_hash():
    h = hash_client_key(ip="1.2.3.4")
    assert len(h) == 16
    assert h == hash_client_key(ip="1.2.3.4")  # deterministic
