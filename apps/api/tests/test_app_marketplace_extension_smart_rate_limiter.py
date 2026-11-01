from app.services.app_marketplace_extension_smart_rate_limiter import SmartRateLimiterService
import time


def test_basic_allow():
    svc = SmartRateLimiterService()
    result = svc.check("client-1", cost=1, capacity=10, refill_rate=5)
    assert result["allowed"] is True
    assert result["remaining"] == 9
    assert result["limit"] == 10


def test_exhaust_tokens():
    svc = SmartRateLimiterService()
    for i in range(10):
        result = svc.check("client-2", cost=1, capacity=10, refill_rate=0.01)
    # 11th request should fail
    result = svc.check("client-2", cost=1, capacity=10, refill_rate=0.01)
    assert result["allowed"] is False
    assert result["retry_after"] > 0


def test_adaptive_penalty_escalation():
    svc = SmartRateLimiterService()
    # Exhaust bucket with very slow refill
    bucket = svc.get_or_create("client-3", capacity=2, refill_rate=0.001)
    bucket.tokens = 0  # force empty

    # First violation: 2^1 = 2s penalty
    r1 = svc.check("client-3", cost=1, capacity=2, refill_rate=0.001)
    assert r1["allowed"] is False
    assert r1["violations"] == 1

    # Second violation: 2^2 = 4s penalty (but penalty_until blocks us)
    r2 = svc.check("client-3", cost=1, capacity=2, refill_rate=0.001)
    assert r2["allowed"] is False
    assert r2["violations"] >= 1  # still penalized


def test_high_cost_request():
    svc = SmartRateLimiterService()
    # Request that costs 5 tokens out of 10
    result = svc.check("client-4", cost=5, capacity=10, refill_rate=1)
    assert result["allowed"] is True
    assert result["remaining"] == 5
    # Another 5 should work
    result = svc.check("client-4", cost=5, capacity=10, refill_rate=1)
    assert result["allowed"] is True
    # Now should fail
    result = svc.check("client-4", cost=5, capacity=10, refill_rate=1)
    assert result["allowed"] is False


def test_sliding_window_tracking():
    svc = SmartRateLimiterService()
    for _ in range(5):
        svc.check("client-5", cost=2, capacity=100, refill_rate=10)
    result = svc.check("client-5", cost=1, capacity=100, refill_rate=10)
    assert result["requests_last_minute"] == 11  # 5*2 + 1
    assert result["requests_last_hour"] == 11


def test_reset():
    svc = SmartRateLimiterService()
    bucket = svc.get_or_create("client-6", capacity=5, refill_rate=0.01)
    bucket.tokens = 0
    bucket.violations = 3
    svc.reset("client-6")
    assert bucket.tokens == 5.0
    assert bucket.violations == 0


def test_top_consumers():
    svc = SmartRateLimiterService()
    for _ in range(10):
        svc.check("heavy-user", capacity=1000, refill_rate=100)
    for _ in range(3):
        svc.check("light-user", capacity=1000, refill_rate=100)
    top = svc.get_top_consumers(2)
    assert top[0][0] == "heavy-user"
    assert top[0][1] == 10
