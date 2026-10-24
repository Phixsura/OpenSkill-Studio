"""Token bucket rate limiter tests."""
import pytest
from app.services.app_rate_bucket import TokenBucket, get_bucket, try_consume, TIER_CONFIGS

def test_bucket_starts_full():
    b = TokenBucket(capacity=10, refill_rate=1.0)
    assert b.available == 10

def test_consume_decreases():
    b = TokenBucket(capacity=10, refill_rate=1.0)
    assert b.consume() is True
    assert b.available == 9

def test_consume_empty():
    b = TokenBucket(capacity=2, refill_rate=0.001)
    assert b.consume() is True
    assert b.consume() is True
    assert b.consume() is False

def test_consume_multiple():
    b = TokenBucket(capacity=10, refill_rate=1.0)
    assert b.consume(5) is True
    assert b.available == 5

def test_consume_over_capacity():
    b = TokenBucket(capacity=5, refill_rate=1.0)
    assert b.consume(10) is False

def test_get_bucket():
    b = get_bucket("test-app-bucket")
    assert b.capacity == TIER_CONFIGS["standard"]["capacity"]

def test_get_bucket_premium():
    b = get_bucket("test-premium", "premium")
    assert b.capacity == TIER_CONFIGS["premium"]["capacity"]

def test_try_consume():
    assert try_consume("try-test-app") is True

@pytest.mark.parametrize("tier", TIER_CONFIGS.keys())
def test_tier_configs(tier):
    b = get_bucket(f"tier-test-{tier}", tier)
    assert b.capacity > 0
    assert b.refill_rate > 0
