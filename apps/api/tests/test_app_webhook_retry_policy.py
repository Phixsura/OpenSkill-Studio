"""Tests for App Webhook Retry Policy — strategies, delays, schedules."""

import pytest

from app.services.app_webhook_retry_policy import AppWebhookRetryPolicy, BackoffStrategy


class TestCreatePolicy:
    def test_create(self):
        p = AppWebhookRetryPolicy()
        pol = p.create_policy("inst-1", "p1", max_retries=3, strategy=BackoffStrategy.EXPONENTIAL)
        assert pol.max_retries == 3

    def test_invalid_retries(self):
        p = AppWebhookRetryPolicy()
        with pytest.raises(ValueError):
            p.create_policy("inst-1", "p1", max_retries=0)


class TestComputeRetry:
    def test_exponential(self):
        p = AppWebhookRetryPolicy()
        p.create_policy("inst-1", "p1", max_retries=10, strategy=BackoffStrategy.EXPONENTIAL, base_delay_seconds=10)
        r0 = p.compute_retry("inst-1", "p1", 0)
        r1 = p.compute_retry("inst-1", "p1", 1)
        r2 = p.compute_retry("inst-1", "p1", 2)
        assert r0.delay_seconds == 10  # 10 * 2^0
        assert r1.delay_seconds == 20  # 10 * 2^1
        assert r2.delay_seconds == 40  # 10 * 2^2

    def test_linear(self):
        p = AppWebhookRetryPolicy()
        p.create_policy("inst-1", "p1", strategy=BackoffStrategy.LINEAR, base_delay_seconds=10)
        r0 = p.compute_retry("inst-1", "p1", 0)
        r1 = p.compute_retry("inst-1", "p1", 1)
        assert r0.delay_seconds == 10
        assert r1.delay_seconds == 20

    def test_fixed(self):
        p = AppWebhookRetryPolicy()
        p.create_policy("inst-1", "p1", strategy=BackoffStrategy.FIXED, base_delay_seconds=30)
        r0 = p.compute_retry("inst-1", "p1", 0)
        r2 = p.compute_retry("inst-1", "p1", 2)
        assert r0.delay_seconds == 30
        assert r2.delay_seconds == 30

    def test_max_delay_cap(self):
        p = AppWebhookRetryPolicy()
        p.create_policy("inst-1", "p1", max_retries=10, strategy=BackoffStrategy.EXPONENTIAL,
                         base_delay_seconds=100, max_delay_seconds=500)
        r = p.compute_retry("inst-1", "p1", 5)  # 100 * 32 = 3200, capped
        assert r.delay_seconds == 500

    def test_exhausted(self):
        p = AppWebhookRetryPolicy()
        p.create_policy("inst-1", "p1", max_retries=3)
        r = p.compute_retry("inst-1", "p1", 3)
        assert r.should_retry is False


class TestFullSchedule:
    def test_schedule(self):
        p = AppWebhookRetryPolicy()
        p.create_policy("inst-1", "p1", max_retries=3, strategy=BackoffStrategy.FIXED, base_delay_seconds=10)
        schedule = p.get_full_schedule("inst-1", "p1")
        assert len(schedule) == 4  # attempts 0,1,2 retry + 3 exhausted
        assert schedule[-1].should_retry is False


class TestIsolation:
    def test_cross_installation(self):
        p = AppWebhookRetryPolicy()
        p.create_policy("inst-1", "p1")
        with pytest.raises(KeyError):
            p.get_policy("inst-2", "p1")
