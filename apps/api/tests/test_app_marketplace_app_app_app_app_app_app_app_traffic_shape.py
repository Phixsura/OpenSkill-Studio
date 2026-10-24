from app.services.app_marketplace_app_app_app_app_app_app_app_traffic_shape import SlidingWindowLimiter

def test_allow_within_limit():
    lim = SlidingWindowLimiter(max_requests=3, window_seconds=60)
    for i in range(3):
        r = lim.allow("user1", now=100.0 + i)
        assert r["allowed"]
    r = lim.allow("user1", now=103.0)
    assert not r["allowed"]
    assert r["remaining"] == 0

def test_burst():
    lim = SlidingWindowLimiter(max_requests=2, window_seconds=60, burst=1)
    for i in range(3):
        assert lim.allow("u1", now=100.0 + i)["allowed"]
    assert not lim.allow("u1", now=103.0)["allowed"]

def test_window_expiry():
    lim = SlidingWindowLimiter(max_requests=1, window_seconds=10)
    lim.allow("u1", now=100.0)
    assert not lim.allow("u1", now=105.0)["allowed"]
    assert lim.allow("u1", now=111.0)["allowed"]  # window expired
