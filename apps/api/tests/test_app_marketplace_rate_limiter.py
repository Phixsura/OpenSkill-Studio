from app.services.app_marketplace_rate_limiter import RateLimiter


def test_allow_within_limit():
    rl = RateLimiter(default_capacity=10, default_refill_rate=0.0)
    for _ in range(10):
        assert rl.allow("key1") is True
    assert rl.allow("key1") is False  # 11th should fail


def test_remaining():
    rl = RateLimiter(default_capacity=5, default_refill_rate=0.0)
    assert rl.remaining("key2") == 5
    rl.allow("key2")
    rl.allow("key2")
    assert rl.remaining("key2") == 3


def test_custom_limit():
    rl = RateLimiter()
    rl.set_limit("vip", capacity=1000, refill_rate=100.0)
    assert rl.remaining("vip") == 1000


def test_stats():
    rl = RateLimiter(default_capacity=3, default_refill_rate=0.0)
    rl.allow("key3")
    rl.allow("key3")
    rl.allow("key3")
    rl.allow("key3")  # denied
    stats = rl.get_stats("key3")
    assert stats["capacity"] == 3
    assert stats["denied_count"] == 1


def test_reset():
    rl = RateLimiter(default_capacity=2, default_refill_rate=0.0)
    rl.allow("key4")
    rl.allow("key4")
    assert rl.allow("key4") is False
    rl.reset("key4")
    assert rl.allow("key4") is True


def test_cost():
    rl = RateLimiter(default_capacity=10, default_refill_rate=0.0)
    assert rl.allow("key5", cost=5) is True
    assert rl.remaining("key5") == 5
    assert rl.allow("key5", cost=6) is False
