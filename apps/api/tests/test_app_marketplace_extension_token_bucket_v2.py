from app.services.app_marketplace_extension_token_bucket_v2 import TokenBucketV2Service


def test_basic_consume():
    tb = TokenBucketV2Service()
    tb.create_bucket("api", capacity=10, refill_rate=1)
    result = tb.consume("api", 3)
    assert result["allowed"] is True
    assert result["remaining"] == 7


def test_exhaustion():
    tb = TokenBucketV2Service()
    tb.create_bucket("api", capacity=5, refill_rate=0.001)
    for _ in range(5):
        tb.consume("api")
    result = tb.consume("api")
    assert result["allowed"] is False
    assert "retry_after_seconds" in result


def test_priority_bypass():
    tb = TokenBucketV2Service()
    tb.create_bucket("api", capacity=1, refill_rate=0.001)
    tb.consume("api")  # exhaust
    result = tb.consume("api", priority="critical")
    assert result["allowed"] is True
    assert result["reason"] == "priority bypass"


def test_overdraft():
    tb = TokenBucketV2Service()
    tb.create_bucket("api", capacity=5, refill_rate=0.001, overdraft_limit=3)
    for _ in range(5):
        tb.consume("api")
    # Should allow overdraft
    result = tb.consume("api", 2)
    assert result["allowed"] is True
    assert result["overdraft"] is True
    assert result["remaining"] < 0


def test_overdraft_exhausted():
    tb = TokenBucketV2Service()
    tb.create_bucket("api", capacity=5, refill_rate=0.001, overdraft_limit=3)
    # Consume all capacity + all overdraft in one shot
    tb.consume("api", 5)  # exhaust capacity
    tb.consume("api", 3)  # exhaust overdraft (tokens now at -3)
    result = tb.consume("api", 1)  # should fail, would go to -4 < -3
    assert result["allowed"] is False


def test_reservation():
    tb = TokenBucketV2Service()
    tb.create_bucket("api", capacity=10, refill_rate=1)
    assert tb.reserve("api", 5, "res-1") is True
    stats = tb.get_stats("api")
    assert stats["tokens"] <= 5


def test_cancel_reservation():
    tb = TokenBucketV2Service()
    tb.create_bucket("api", capacity=10, refill_rate=1)
    tb.reserve("api", 5, "res-1")
    tb.cancel_reservation("api", "res-1")
    stats = tb.get_stats("api")
    assert stats["tokens"] == 10


def test_multi_bucket():
    tb = TokenBucketV2Service()
    tb.create_bucket("global", capacity=100, refill_rate=10)
    tb.create_bucket("per_user", capacity=10, refill_rate=1)
    result = tb.multi_bucket_consume(["global", "per_user"], 1)
    assert result["allowed"] is True
    assert result["buckets_checked"] == 2


def test_multi_bucket_blocked():
    tb = TokenBucketV2Service()
    tb.create_bucket("global", capacity=100, refill_rate=10)
    tb.create_bucket("per_user", capacity=1, refill_rate=0.001)
    tb.consume("per_user")  # exhaust per_user
    result = tb.multi_bucket_consume(["global", "per_user"])
    assert result["allowed"] is False
    assert result["blocking_bucket"] == "per_user"


def test_stats():
    tb = TokenBucketV2Service()
    tb.create_bucket("api", capacity=10, refill_rate=1)
    tb.consume("api", 3)
    stats = tb.get_stats("api")
    assert stats["total_allowed"] == 1
    assert stats["utilization"] > 0
