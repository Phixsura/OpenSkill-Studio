"""Tests for Endpoint Rate Limit Policy service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_rate_limit_policy import (
    RateLimitPolicyManager, RateLimitPolicy,
)


class TestRateLimitPolicyManager:
    def test_allow_under_limit(self):
        svc = RateLimitPolicyManager()
        svc.set_policy(RateLimitPolicy("p1", "ep1", 60.0, 10))
        result = svc.check("ep1", "c1", 100.0)
        assert result["allowed"] is True
        assert result["remaining"] == 9

    def test_deny_over_limit(self):
        svc = RateLimitPolicyManager()
        svc.set_policy(RateLimitPolicy("p1", "ep1", 60.0, 3))
        for t in range(3):
            svc.check("ep1", "c1", 100.0 + t)
        result = svc.check("ep1", "c1", 103.0)
        assert result["allowed"] is False
        assert result["reason"] == "rate_limited"

    def test_sliding_window_expiry(self):
        svc = RateLimitPolicyManager()
        svc.set_policy(RateLimitPolicy("p1", "ep1", 10.0, 2))
        svc.check("ep1", "c1", 100.0)
        svc.check("ep1", "c1", 105.0)
        # At t=115, first request expired
        result = svc.check("ep1", "c1", 115.0)
        assert result["allowed"] is True

    def test_burst(self):
        svc = RateLimitPolicyManager()
        svc.set_policy(RateLimitPolicy("p1", "ep1", 60.0, 2, burst_limit=1))
        svc.check("ep1", "c1", 100.0)
        svc.check("ep1", "c1", 101.0)
        result = svc.check("ep1", "c1", 102.0)
        assert result["allowed"] is True
        assert result["burst"] is True

    def test_burst_exhausted(self):
        svc = RateLimitPolicyManager()
        svc.set_policy(RateLimitPolicy("p1", "ep1", 60.0, 1, burst_limit=1))
        svc.check("ep1", "c1", 100.0)
        svc.check("ep1", "c1", 101.0)  # burst
        result = svc.check("ep1", "c1", 102.0)
        assert result["allowed"] is False

    def test_no_policy_allows(self):
        svc = RateLimitPolicyManager()
        result = svc.check("no_policy_ep", "c1", 100.0)
        assert result["allowed"] is True

    def test_consumer_isolation(self):
        svc = RateLimitPolicyManager()
        svc.set_policy(RateLimitPolicy("p1", "ep1", 60.0, 2))
        svc.check("ep1", "c1", 100.0)
        svc.check("ep1", "c1", 101.0)
        # c2 should still be allowed
        result = svc.check("ep1", "c2", 102.0)
        assert result["allowed"] is True

    def test_usage(self):
        svc = RateLimitPolicyManager()
        svc.set_policy(RateLimitPolicy("p1", "ep1", 60.0, 10))
        svc.check("ep1", "c1", 100.0)
        usage = svc.get_consumer_usage("ep1", "c1", 100.0)
        assert usage["current"] == 1
        assert usage["usage_pct"] == 10.0

    def test_stats(self):
        svc = RateLimitPolicyManager()
        svc.set_policy(RateLimitPolicy("p1", "ep1", 60.0, 1))
        svc.check("ep1", "c1", 100.0)
        svc.check("ep1", "c1", 101.0)  # denied
        stats = svc.get_stats()
        assert stats["total_allowed"] == 1
        assert stats["total_denied"] == 1

    def test_invalid_policy(self):
        svc = RateLimitPolicyManager()
        with pytest.raises(ValueError):
            svc.set_policy(RateLimitPolicy("p1", "ep1", 60.0, 0))

    def test_instance_isolation(self):
        a, b = RateLimitPolicyManager(), RateLimitPolicyManager()
        a.set_policy(RateLimitPolicy("p1", "ep1", 60.0, 10))
        assert b.check("ep1", "c1", 100.0)["reason"] == "no_policy"
