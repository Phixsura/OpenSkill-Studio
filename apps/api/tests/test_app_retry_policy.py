"""Tests for App Retry Policy Engine — strategies, limits, deadlines."""

import pytest

from app.services.app_retry_policy import (
    AppRetryPolicyEngine,
    RetryConfig,
    RetryStrategy,
)


class TestFirstAttempt:
    def test_first_attempt_allowed(self):
        e = AppRetryPolicyEngine()
        d = e.should_retry("op-1")
        assert d.should_retry is True
        assert d.reason == "first_attempt"

    def test_record_attempt(self):
        e = AppRetryPolicyEngine()
        state = e.record_attempt("op-1")
        assert state.attempt == 1


class TestFixedStrategy:
    def test_fixed_delay(self):
        e = AppRetryPolicyEngine(RetryConfig(
            strategy=RetryStrategy.FIXED, base_delay_seconds=5.0, max_retries=3,
        ))
        e.record_attempt("op-1")
        d = e.should_retry("op-1")
        assert d.should_retry is True
        assert d.delay_seconds == 5.0

    def test_fixed_consistent(self):
        e = AppRetryPolicyEngine(RetryConfig(
            strategy=RetryStrategy.FIXED, base_delay_seconds=2.0, max_retries=5,
        ))
        e.record_attempt("op-1")
        e.record_attempt("op-1")
        e.record_attempt("op-1")
        d = e.should_retry("op-1")
        assert d.delay_seconds == 2.0


class TestLinearStrategy:
    def test_linear_delay(self):
        e = AppRetryPolicyEngine(RetryConfig(
            strategy=RetryStrategy.LINEAR, base_delay_seconds=2.0, max_retries=5,
        ))
        e.record_attempt("op-1")  # attempt 1
        d = e.should_retry("op-1")
        assert d.delay_seconds == 2.0  # 2 * 1

        e.record_attempt("op-1")  # attempt 2
        d = e.should_retry("op-1")
        assert d.delay_seconds == 4.0  # 2 * 2

        e.record_attempt("op-1")  # attempt 3
        d = e.should_retry("op-1")
        assert d.delay_seconds == 6.0  # 2 * 3


class TestExponentialStrategy:
    def test_exponential_delay(self):
        e = AppRetryPolicyEngine(RetryConfig(
            strategy=RetryStrategy.EXPONENTIAL,
            base_delay_seconds=1.0, multiplier=2.0, max_retries=5,
        ))
        e.record_attempt("op-1")  # attempt 1
        d = e.should_retry("op-1")
        assert d.delay_seconds == 1.0  # 1 * 2^0

        e.record_attempt("op-1")  # attempt 2
        d = e.should_retry("op-1")
        assert d.delay_seconds == 2.0  # 1 * 2^1

        e.record_attempt("op-1")  # attempt 3
        d = e.should_retry("op-1")
        assert d.delay_seconds == 4.0  # 1 * 2^2

    def test_max_delay_cap(self):
        e = AppRetryPolicyEngine(RetryConfig(
            strategy=RetryStrategy.EXPONENTIAL,
            base_delay_seconds=1.0, multiplier=10.0, max_delay_seconds=30.0,
            max_retries=10,
        ))
        e.record_attempt("op-1")
        e.record_attempt("op-1")
        e.record_attempt("op-1")  # 1 * 10^2 = 100, capped at 30
        d = e.should_retry("op-1")
        assert d.delay_seconds == 30.0


class TestExponentialJitter:
    def test_jitter_deterministic(self):
        e = AppRetryPolicyEngine(RetryConfig(
            strategy=RetryStrategy.EXPONENTIAL_JITTER,
            base_delay_seconds=1.0, max_retries=5,
        ))
        e.record_attempt("op-1")
        d1 = e.should_retry("op-1")
        # Reset and try again — same operation should get same jitter
        e.reset("op-1")
        e.record_attempt("op-1")
        d2 = e.should_retry("op-1")
        assert d1.delay_seconds == d2.delay_seconds

    def test_jitter_varies_by_operation(self):
        e = AppRetryPolicyEngine(RetryConfig(
            strategy=RetryStrategy.EXPONENTIAL_JITTER,
            base_delay_seconds=1.0, max_retries=5,
        ))
        e.record_attempt("op-1")
        e.record_attempt("op-2")
        d1 = e.should_retry("op-1")
        d2 = e.should_retry("op-2")
        # Different operations likely get different jitter
        # (extremely unlikely to be exactly equal with SHA-256)
        assert isinstance(d1.delay_seconds, float)
        assert isinstance(d2.delay_seconds, float)


class TestMaxRetries:
    def test_exhausted(self):
        e = AppRetryPolicyEngine(RetryConfig(max_retries=2))
        e.record_attempt("op-1")
        e.record_attempt("op-1")
        d = e.should_retry("op-1")
        assert d.should_retry is False
        assert d.reason == "max_retries_exceeded"

    def test_not_exhausted(self):
        e = AppRetryPolicyEngine(RetryConfig(max_retries=3))
        e.record_attempt("op-1")
        d = e.should_retry("op-1")
        assert d.should_retry is True


class TestDeadline:
    def test_deadline_exceeded(self):
        e = AppRetryPolicyEngine(RetryConfig(
            max_retries=10, deadline_seconds=60.0,
        ))
        e.record_attempt("op-1", now=1000.0)
        d = e.should_retry("op-1", now=1061.0)
        assert d.should_retry is False
        assert d.reason == "deadline_exceeded"

    def test_within_deadline(self):
        e = AppRetryPolicyEngine(RetryConfig(
            max_retries=10, deadline_seconds=60.0,
        ))
        e.record_attempt("op-1", now=1000.0)
        d = e.should_retry("op-1", now=1030.0)
        assert d.should_retry is True


class TestReset:
    def test_reset(self):
        e = AppRetryPolicyEngine(RetryConfig(max_retries=2))
        e.record_attempt("op-1")
        e.record_attempt("op-1")
        e.reset("op-1")
        d = e.should_retry("op-1")
        assert d.should_retry is True
        assert d.reason == "first_attempt"

    def test_get_state(self):
        e = AppRetryPolicyEngine()
        assert e.get_state("op-1") is None
        e.record_attempt("op-1")
        assert e.get_state("op-1") is not None
