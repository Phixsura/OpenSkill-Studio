"""Tests for Rate Plan Manager service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_rate_plan_manager import (
    RatePlanManager, RatePlan,
)


class TestRatePlanManager:
    def test_create_and_list(self):
        svc = RatePlanManager()
        svc.create_plan(RatePlan("free", "Free", 60, 1000))
        svc.create_plan(RatePlan("pro", "Pro", 300, 50000, burst_size=50, price_cents=2999))
        plans = svc.list_plans()
        assert len(plans) == 2
        assert plans[0]["name"] == "Free"
        assert plans[1]["name"] == "Pro"

    def test_assign_and_check(self):
        svc = RatePlanManager()
        svc.create_plan(RatePlan("basic", "Basic", 10, 1000))
        svc.assign_plan("c1", "basic")
        result = svc.check_limit("c1")
        assert result["allowed"] is True
        assert result["used_burst"] is False

    def test_minute_limit(self):
        svc = RatePlanManager()
        svc.create_plan(RatePlan("tiny", "Tiny", 2, 1000))
        svc.assign_plan("c1", "tiny")
        svc.check_limit("c1")
        svc.check_limit("c1")
        result = svc.check_limit("c1")
        assert result["allowed"] is False
        assert result["reason"] == "minute_limit"

    def test_burst_allowance(self):
        svc = RatePlanManager()
        svc.create_plan(RatePlan("burst", "Burst", 1, 1000, burst_size=2))
        svc.assign_plan("c1", "burst")
        svc.check_limit("c1")  # normal
        r2 = svc.check_limit("c1")  # burst
        assert r2["allowed"] is True
        assert r2["used_burst"] is True
        assert r2["burst_remaining"] == 1

    def test_daily_limit(self):
        svc = RatePlanManager()
        svc.create_plan(RatePlan("micro", "Micro", 100, 3))
        svc.assign_plan("c1", "micro")
        for _ in range(3):
            svc.check_limit("c1")
        result = svc.check_limit("c1")
        assert result["allowed"] is False
        assert result["reason"] == "daily_limit"

    def test_no_plan(self):
        svc = RatePlanManager()
        assert svc.check_limit("unknown")["reason"] == "no_plan"

    def test_usage(self):
        svc = RatePlanManager()
        svc.create_plan(RatePlan("std", "Standard", 100, 10000))
        svc.assign_plan("c1", "std")
        svc.check_limit("c1")
        usage = svc.get_usage("c1")
        assert usage["minute_usage"] == "1/100"
        assert usage["minute_pct"] == 1.0

    def test_reset_minute(self):
        svc = RatePlanManager()
        svc.create_plan(RatePlan("t", "T", 2, 1000, burst_size=1))
        svc.assign_plan("c1", "t")
        svc.check_limit("c1")
        svc.check_limit("c1")
        assert svc.check_limit("c1")["used_burst"] is True
        svc.reset_minute("c1")
        r = svc.check_limit("c1")
        assert r["allowed"] is True
        assert r["used_burst"] is False

    def test_duplicate_plan(self):
        svc = RatePlanManager()
        svc.create_plan(RatePlan("p1", "P1", 10, 100))
        with pytest.raises(ValueError):
            svc.create_plan(RatePlan("p1", "P1 dup", 20, 200))

    def test_isolation(self):
        a, b = RatePlanManager(), RatePlanManager()
        a.create_plan(RatePlan("x", "X", 10, 100))
        assert b.list_plans() == []
