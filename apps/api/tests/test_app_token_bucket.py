"""Tests for App Token Bucket — consume, refill, capacity."""

import pytest

from app.services.app_token_bucket import AppTokenBucket


class TestCreate:
    def test_create(self):
        t = AppTokenBucket()
        b = t.create_bucket("inst-1", "api", capacity=50, refill_rate=5.0)
        assert b.capacity == 50
        assert t.available("inst-1", "api") == 50

    def test_invalid_capacity(self):
        t = AppTokenBucket()
        with pytest.raises(ValueError):
            t.create_bucket("inst-1", "api", capacity=0)


class TestConsume:
    def test_consume_success(self):
        t = AppTokenBucket()
        t.create_bucket("inst-1", "api", capacity=10)
        assert t.consume("inst-1", "api", 5) is True
        assert t.available("inst-1", "api") == 5

    def test_consume_fail(self):
        t = AppTokenBucket()
        t.create_bucket("inst-1", "api", capacity=3, refill_rate=0.001)
        t.consume("inst-1", "api", 3)
        assert t.consume("inst-1", "api", 1) is False

    def test_consume_batch(self):
        t = AppTokenBucket()
        t.create_bucket("inst-1", "api", capacity=100)
        assert t.consume("inst-1", "api", 50) is True
        assert t.consume("inst-1", "api", 60) is False


class TestReset:
    def test_reset(self):
        t = AppTokenBucket()
        t.create_bucket("inst-1", "api", capacity=100, refill_rate=0.001)
        t.consume("inst-1", "api", 90)
        b = t.reset("inst-1", "api")
        assert t.available("inst-1", "api") == 100


class TestIsolation:
    def test_cross(self):
        t = AppTokenBucket()
        t.create_bucket("inst-1", "api", capacity=10)
        assert t.list_buckets("inst-2") == []
