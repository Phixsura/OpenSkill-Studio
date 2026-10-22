from app.services.app_marketplace_app_rate_limiter_middleware import SlidingWindowRateLimiter

def test_allowed():
    rl = SlidingWindowRateLimiter(limit=10, window_seconds=60)
    r = rl.is_allowed("app1")
    assert r["allowed"]
    assert r["remaining"] == 9

def test_exceeded():
    rl = SlidingWindowRateLimiter(limit=3, window_seconds=60)
    rl.is_allowed("app1")
    rl.is_allowed("app1")
    rl.is_allowed("app1")
    r = rl.is_allowed("app1")
    assert not r["allowed"]
    assert r["remaining"] == 0

def test_separate_keys():
    rl = SlidingWindowRateLimiter(limit=2, window_seconds=60)
    rl.is_allowed("app1")
    rl.is_allowed("app1")
    r = rl.is_allowed("app2")
    assert r["allowed"]

def test_usage():
    rl = SlidingWindowRateLimiter(limit=100, window_seconds=60)
    rl.is_allowed("app1")
    rl.is_allowed("app1")
    u = rl.get_usage("app1")
    assert u["current"] == 2
