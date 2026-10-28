"""Tests for App Circuit Breaker — state transitions, cooldown."""

import pytest

from app.services.app_circuit_breaker import AppCircuitBreaker, BreakerState


class TestCreate:
    def test_create(self):
        c = AppCircuitBreaker()
        cb = c.create("inst-1", "cb1", "payment-api", failure_threshold=3)
        assert cb.state == BreakerState.CLOSED
        assert cb.failure_threshold == 3


class TestTransitions:
    def test_closed_to_open(self):
        c = AppCircuitBreaker()
        c.create("inst-1", "cb1", "api", failure_threshold=3)
        c.record_failure("inst-1", "cb1")
        c.record_failure("inst-1", "cb1")
        cb = c.record_failure("inst-1", "cb1")
        assert cb.state == BreakerState.OPEN

    def test_open_blocks(self):
        c = AppCircuitBreaker()
        c.create("inst-1", "cb1", "api", failure_threshold=1)
        c.record_failure("inst-1", "cb1")
        assert c.is_allowed("inst-1", "cb1") is False

    def test_half_open_on_cooldown(self):
        c = AppCircuitBreaker()
        c.create("inst-1", "cb1", "api", failure_threshold=1, cooldown_seconds=0)
        c.record_failure("inst-1", "cb1")
        # Cooldown is 0, so should transition to half_open
        assert c.is_allowed("inst-1", "cb1") is True
        assert c.get_state("inst-1", "cb1") == BreakerState.HALF_OPEN

    def test_half_open_success_closes(self):
        c = AppCircuitBreaker()
        c.create("inst-1", "cb1", "api", failure_threshold=1, cooldown_seconds=0)
        c.record_failure("inst-1", "cb1")
        c.is_allowed("inst-1", "cb1")  # triggers half_open
        cb = c.record_success("inst-1", "cb1")
        assert cb.state == BreakerState.CLOSED

    def test_half_open_failure_reopens(self):
        c = AppCircuitBreaker()
        c.create("inst-1", "cb1", "api", failure_threshold=1, cooldown_seconds=0)
        c.record_failure("inst-1", "cb1")
        c.is_allowed("inst-1", "cb1")  # triggers half_open
        cb = c.record_failure("inst-1", "cb1")
        assert cb.state == BreakerState.OPEN


class TestReset:
    def test_manual_reset(self):
        c = AppCircuitBreaker()
        c.create("inst-1", "cb1", "api", failure_threshold=1)
        c.record_failure("inst-1", "cb1")
        cb = c.reset("inst-1", "cb1")
        assert cb.state == BreakerState.CLOSED


class TestIsolation:
    def test_cross(self):
        c = AppCircuitBreaker()
        c.create("inst-1", "cb1", "api")
        assert c.list_breakers("inst-2") == []
