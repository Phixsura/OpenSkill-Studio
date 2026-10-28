"""Tests for App Token Bucket — consume, refill, burst, retry-after."""

import pytest

from app.services.app_token_bucket import AppTokenBucket


class TestInit:
    def test_invalid_capacity(self):
        with pytest.raises(ValueError):
            AppTokenBucket(capacity=0)

    def test_invalid_rate(self):
        with pytest.raises(ValueError):
            AppTokenBucket(refill_rate=0)


class TestConsume:
    def test_first_consume(self):
        b = AppTokenBucket(capacity=10, refill_rate=1)
        r = b.consume("k1", 1, now=1000.0)
        assert r.allowed is True
        assert r.tokens_remaining == 9

    def test_consume_multiple(self):
        b = AppTokenBucket(capacity=10, refill_rate=1)
        r = b.consume("k1", 5, now=1000.0)
        assert r.allowed is True
        assert r.tokens_remaining == 5

    def test_consume_all(self):
        b = AppTokenBucket(capacity=5, refill_rate=1)
        r = b.consume("k1", 5, now=1000.0)
        assert r.allowed is True
        assert r.tokens_remaining == 0

    def test_consume_over_capacity(self):
        b = AppTokenBucket(capacity=5, refill_rate=1)
        r = b.consume("k1", 6, now=1000.0)
        assert r.allowed is False
        assert r.retry_after_seconds > 0

    def test_exhausted_then_denied(self):
        b = AppTokenBucket(capacity=3, refill_rate=1)
        b.consume("k1", 3, now=1000.0)
        r = b.consume("k1", 1, now=1000.0)
        assert r.allowed is False

    def test_negative_tokens_rejected(self):
        b = AppTokenBucket(capacity=10, refill_rate=1)
        with pytest.raises(ValueError):
            b.consume("k1", 0)


class TestRefill:
    def test_refill_after_wait(self):
        b = AppTokenBucket(capacity=10, refill_rate=2)
        b.consume("k1", 10, now=1000.0)  # empty
        r = b.consume("k1", 1, now=1001.0)  # 1s later → 2 tokens refilled
        assert r.allowed is True

    def test_refill_caps_at_capacity(self):
        b = AppTokenBucket(capacity=10, refill_rate=100)
        b.consume("k1", 5, now=1000.0)
        state = b.peek("k1", now=1010.0)  # 10s * 100/s = way over capacity
        assert state.tokens == 10  # capped

    def test_partial_refill(self):
        b = AppTokenBucket(capacity=10, refill_rate=2)
        b.consume("k1", 10, now=1000.0)
        r = b.consume("k1", 1, now=1000.3)  # 0.3s → 0.6 tokens
        assert r.allowed is False  # 0.6 < 1

    def test_exact_refill(self):
        b = AppTokenBucket(capacity=10, refill_rate=10)
        b.consume("k1", 10, now=1000.0)
        r = b.consume("k1", 5, now=1000.5)  # 0.5s * 10/s = 5 tokens
        assert r.allowed is True
        assert r.tokens_remaining == pytest.approx(0.0, abs=0.01)


class TestRetryAfter:
    def test_retry_time(self):
        b = AppTokenBucket(capacity=10, refill_rate=5)
        b.consume("k1", 10, now=1000.0)
        r = b.consume("k1", 5, now=1000.0)
        # Need 5 tokens, refill at 5/s → 1 second
        assert r.retry_after_seconds == pytest.approx(1.0, abs=0.01)

    def test_retry_zero_when_allowed(self):
        b = AppTokenBucket(capacity=10, refill_rate=1)
        r = b.consume("k1", 1, now=1000.0)
        assert r.retry_after_seconds == 0


class TestKeyIsolation:
    def test_independent_keys(self):
        b = AppTokenBucket(capacity=5, refill_rate=1)
        b.consume("k1", 5, now=1000.0)
        r = b.consume("k2", 1, now=1000.0)
        assert r.allowed is True  # k2 has full bucket


class TestPeek:
    def test_peek_doesnt_consume(self):
        b = AppTokenBucket(capacity=10, refill_rate=1)
        s1 = b.peek("k1", now=1000.0)
        s2 = b.peek("k1", now=1000.0)
        assert s1.tokens == s2.tokens == 10

    def test_peek_refills(self):
        b = AppTokenBucket(capacity=10, refill_rate=5)
        b.consume("k1", 10, now=1000.0)
        s = b.peek("k1", now=1001.0)
        assert s.tokens == pytest.approx(5.0)


class TestReset:
    def test_reset_restores(self):
        b = AppTokenBucket(capacity=10, refill_rate=1)
        b.consume("k1", 10, now=1000.0)
        b.reset("k1")
        r = b.consume("k1", 10, now=1000.0)
        assert r.allowed is True
