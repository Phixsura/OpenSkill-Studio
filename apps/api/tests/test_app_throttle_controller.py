"""Tests for App Throttle Controller — load levels, throughput, allow/deny."""

import pytest

from app.services.app_throttle_controller import (
    AppThrottleController,
    LoadLevel,
    ThrottleConfig,
)


class TestLoadLevels:
    def test_low_load(self):
        c = AppThrottleController()
        s = c.update_load("inst-1", 0.3)
        assert s.load_level == LoadLevel.LOW
        assert s.throttle_pct == 100.0

    def test_medium_load(self):
        c = AppThrottleController()
        s = c.update_load("inst-1", 0.75)
        assert s.load_level == LoadLevel.MEDIUM
        assert s.throttle_pct == 75.0

    def test_high_load(self):
        c = AppThrottleController()
        s = c.update_load("inst-1", 0.9)
        assert s.load_level == LoadLevel.HIGH
        assert s.throttle_pct == 50.0

    def test_critical_load(self):
        c = AppThrottleController()
        s = c.update_load("inst-1", 0.96)
        assert s.load_level == LoadLevel.CRITICAL
        assert s.throttle_pct == 10.0


class TestAllowedRPS:
    def test_full_at_low(self):
        c = AppThrottleController(ThrottleConfig(max_rps=500))
        s = c.update_load("inst-1", 0.1)
        assert s.allowed_rps == 500.0

    def test_reduced_at_high(self):
        c = AppThrottleController(ThrottleConfig(max_rps=1000, high_pct=50))
        s = c.update_load("inst-1", 0.9)
        assert s.allowed_rps == 500.0

    def test_minimal_at_critical(self):
        c = AppThrottleController(ThrottleConfig(max_rps=1000, critical_pct=10))
        s = c.update_load("inst-1", 0.98)
        assert s.allowed_rps == 100.0


class TestShouldAllow:
    def test_allow_under_limit(self):
        c = AppThrottleController(ThrottleConfig(max_rps=100))
        c.update_load("inst-1", 0.1)
        assert c.should_allow("inst-1", 50) is True

    def test_deny_over_limit(self):
        c = AppThrottleController(ThrottleConfig(max_rps=100, high_pct=50))
        c.update_load("inst-1", 0.9)
        assert c.should_allow("inst-1", 60) is False  # limit is 50


class TestEdgeCases:
    def test_load_clamped_above_1(self):
        c = AppThrottleController()
        s = c.update_load("inst-1", 1.5)
        assert s.current_load == 1.0

    def test_load_clamped_below_0(self):
        c = AppThrottleController()
        s = c.update_load("inst-1", -0.5)
        assert s.current_load == 0.0

    def test_missing_installation_id(self):
        c = AppThrottleController()
        with pytest.raises(ValueError):
            c.update_load("", 0.5)


class TestGetState:
    def test_default_state(self):
        c = AppThrottleController()
        s = c.get_state("inst-1")
        assert s.load_level == LoadLevel.LOW
        assert s.current_load == 0.0

    def test_persists_load(self):
        c = AppThrottleController()
        c.update_load("inst-1", 0.8)
        s = c.get_state("inst-1")
        assert s.load_level == LoadLevel.MEDIUM


class TestReset:
    def test_reset(self):
        c = AppThrottleController()
        c.update_load("inst-1", 0.95)
        c.reset_load("inst-1")
        s = c.get_state("inst-1")
        assert s.load_level == LoadLevel.LOW


class TestIsolation:
    def test_independent_installations(self):
        c = AppThrottleController()
        c.update_load("inst-1", 0.95)
        s = c.get_state("inst-2")
        assert s.load_level == LoadLevel.LOW
