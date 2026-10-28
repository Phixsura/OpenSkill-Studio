"""Tests for App Circuit Breaker — state transitions, thresholds, recovery."""

import pytest

from app.services.app_circuit_breaker import (
    AppCircuitBreaker,
    BreakerConfig,
    BreakerState,
)


class TestClosedState:
    def test_starts_closed(self):
        cb = AppCircuitBreaker()
        assert cb.can_execute("svc-1") is True
        assert cb.get_status("svc-1").state == BreakerState.CLOSED

    def test_success_stays_closed(self):
        cb = AppCircuitBreaker()
        cb.record_success("svc-1")
        assert cb.get_status("svc-1").state == BreakerState.CLOSED

    def test_few_failures_stays_closed(self):
        cb = AppCircuitBreaker(BreakerConfig(failure_threshold=5))
        for _ in range(4):
            cb.record_failure("svc-1")
        assert cb.get_status("svc-1").state == BreakerState.CLOSED

    def test_success_resets_failure_count(self):
        cb = AppCircuitBreaker(BreakerConfig(failure_threshold=5))
        for _ in range(4):
            cb.record_failure("svc-1")
        cb.record_success("svc-1")
        assert cb.get_status("svc-1").failure_count == 0


class TestOpenState:
    def test_opens_at_threshold(self):
        cb = AppCircuitBreaker(BreakerConfig(failure_threshold=3))
        for _ in range(3):
            cb.record_failure("svc-1", now=1000.0)
        assert cb.get_status("svc-1").state == BreakerState.OPEN

    def test_open_blocks_execution(self):
        cb = AppCircuitBreaker(BreakerConfig(failure_threshold=2, recovery_timeout=60))
        cb.record_failure("svc-1", now=1000.0)
        cb.record_failure("svc-1", now=1000.0)
        assert cb.can_execute("svc-1", now=1001.0) is False

    def test_open_records_opened_at(self):
        cb = AppCircuitBreaker(BreakerConfig(failure_threshold=2))
        cb.record_failure("svc-1", now=1000.0)
        cb.record_failure("svc-1", now=1001.0)
        assert cb.get_status("svc-1").opened_at == 1001.0


class TestHalfOpenState:
    def test_transitions_after_timeout(self):
        cb = AppCircuitBreaker(BreakerConfig(failure_threshold=2, recovery_timeout=10))
        cb.record_failure("svc-1", now=1000.0)
        cb.record_failure("svc-1", now=1000.0)
        # After recovery timeout
        assert cb.can_execute("svc-1", now=1011.0) is True
        assert cb.get_status("svc-1").state == BreakerState.HALF_OPEN

    def test_success_closes(self):
        cb = AppCircuitBreaker(BreakerConfig(failure_threshold=2, recovery_timeout=10, success_threshold=2))
        cb.record_failure("svc-1", now=1000.0)
        cb.record_failure("svc-1", now=1000.0)
        cb.can_execute("svc-1", now=1011.0)  # → half-open
        cb.record_success("svc-1")
        cb.record_success("svc-1")
        assert cb.get_status("svc-1").state == BreakerState.CLOSED

    def test_failure_reopens(self):
        cb = AppCircuitBreaker(BreakerConfig(failure_threshold=2, recovery_timeout=10))
        cb.record_failure("svc-1", now=1000.0)
        cb.record_failure("svc-1", now=1000.0)
        cb.can_execute("svc-1", now=1011.0)  # → half-open
        cb.record_failure("svc-1", now=1012.0)
        assert cb.get_status("svc-1").state == BreakerState.OPEN

    def test_partial_success_stays_half_open(self):
        cb = AppCircuitBreaker(BreakerConfig(failure_threshold=2, recovery_timeout=10, success_threshold=3))
        cb.record_failure("svc-1", now=1000.0)
        cb.record_failure("svc-1", now=1000.0)
        cb.can_execute("svc-1", now=1011.0)
        cb.record_success("svc-1")
        assert cb.get_status("svc-1").state == BreakerState.HALF_OPEN


class TestServiceIsolation:
    def test_independent_services(self):
        cb = AppCircuitBreaker(BreakerConfig(failure_threshold=2))
        cb.record_failure("svc-1", now=1000.0)
        cb.record_failure("svc-1", now=1000.0)
        assert cb.can_execute("svc-1", now=1000.0) is False
        assert cb.can_execute("svc-2", now=1000.0) is True


class TestReset:
    def test_manual_reset(self):
        cb = AppCircuitBreaker(BreakerConfig(failure_threshold=2))
        cb.record_failure("svc-1")
        cb.record_failure("svc-1")
        cb.reset("svc-1")
        assert cb.get_status("svc-1").state == BreakerState.CLOSED
        assert cb.get_status("svc-1").failure_count == 0
        assert cb.can_execute("svc-1") is True


class TestStatus:
    def test_status_fields(self):
        cb = AppCircuitBreaker(BreakerConfig(failure_threshold=3))
        cb.record_failure("svc-1", now=1000.0)
        s = cb.get_status("svc-1")
        assert s.service == "svc-1"
        assert s.failure_count == 1
        assert s.last_failure_at == 1000.0
        assert s.config.failure_threshold == 3
