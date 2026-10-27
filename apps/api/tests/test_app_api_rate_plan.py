"""Tests for App API Rate Plan — tiers, usage, upgrade/downgrade, overage."""

import pytest

from app.services.app_api_rate_plan import (
    AppApiRatePlan,
    PlanTier,
)


class TestAssignment:
    def test_assign_plan(self):
        rp = AppApiRatePlan()
        a = rp.assign("app-1", PlanTier.STARTER)
        assert a.tier == PlanTier.STARTER

    def test_default_free(self):
        rp = AppApiRatePlan()
        limits = rp.get_limits("unassigned-app")
        assert limits.requests_per_second == 2  # free tier

    def test_get_assignment(self):
        rp = AppApiRatePlan()
        rp.assign("app-1", PlanTier.GROWTH)
        a = rp.get_assignment("app-1")
        assert a is not None
        assert a.tier == PlanTier.GROWTH

    def test_list_by_tier(self):
        rp = AppApiRatePlan()
        rp.assign("a1", PlanTier.FREE)
        rp.assign("a2", PlanTier.STARTER)
        rp.assign("a3", PlanTier.FREE)
        free = rp.list_assignments(PlanTier.FREE)
        assert len(free) == 2


class TestLimits:
    def test_free_limits(self):
        rp = AppApiRatePlan()
        rp.assign("app-1", PlanTier.FREE)
        l = rp.get_limits("app-1")
        assert l.daily_quota == 5_000
        assert l.requests_per_second == 2

    def test_enterprise_limits(self):
        rp = AppApiRatePlan()
        rp.assign("app-1", PlanTier.ENTERPRISE)
        l = rp.get_limits("app-1")
        assert l.daily_quota == 2_000_000
        assert l.requests_per_second == 200

    def test_tiers_ordered(self):
        rp = AppApiRatePlan()
        for tier in (PlanTier.FREE, PlanTier.STARTER, PlanTier.GROWTH, PlanTier.ENTERPRISE):
            rp.assign(tier.value, tier)
        quotas = [rp.get_limits(t.value).daily_quota for t in
                  (PlanTier.FREE, PlanTier.STARTER, PlanTier.GROWTH, PlanTier.ENTERPRISE)]
        assert quotas == sorted(quotas)


class TestUsage:
    def test_record_usage(self):
        rp = AppApiRatePlan()
        rp.assign("app-1", PlanTier.FREE)
        result = rp.record_usage("app-1", 100)
        assert result.allowed is True
        assert result.current_usage == 100
        assert result.remaining == 4900

    def test_quota_exceeded(self):
        rp = AppApiRatePlan()
        rp.assign("app-1", PlanTier.FREE)
        rp.record_usage("app-1", 5000)
        result = rp.record_usage("app-1", 1)
        assert result.allowed is False
        assert result.remaining == 0

    def test_overage_counted(self):
        rp = AppApiRatePlan()
        rp.assign("app-1", PlanTier.FREE)
        rp.record_usage("app-1", 5001)
        a = rp.get_assignment("app-1")
        assert a.overages == 1

    def test_usage_ratio(self):
        rp = AppApiRatePlan()
        rp.assign("app-1", PlanTier.FREE)
        rp.record_usage("app-1", 2500)
        ratio = rp.get_usage_ratio("app-1")
        assert ratio == pytest.approx(50.0)

    def test_daily_usage(self):
        rp = AppApiRatePlan()
        rp.assign("app-1", PlanTier.FREE)
        rp.record_usage("app-1", 100)
        rp.record_usage("app-1", 200)
        assert rp.get_daily_usage("app-1") == 300


class TestUpgradeDowngrade:
    def test_upgrade(self):
        rp = AppApiRatePlan()
        rp.assign("app-1", PlanTier.FREE)
        a = rp.upgrade("app-1", PlanTier.STARTER)
        assert a.tier == PlanTier.STARTER

    def test_upgrade_same_tier_blocked(self):
        rp = AppApiRatePlan()
        rp.assign("app-1", PlanTier.STARTER)
        with pytest.raises(ValueError, match="Cannot upgrade"):
            rp.upgrade("app-1", PlanTier.STARTER)

    def test_upgrade_lower_tier_blocked(self):
        rp = AppApiRatePlan()
        rp.assign("app-1", PlanTier.GROWTH)
        with pytest.raises(ValueError, match="Cannot upgrade"):
            rp.upgrade("app-1", PlanTier.FREE)

    def test_downgrade(self):
        rp = AppApiRatePlan()
        rp.assign("app-1", PlanTier.ENTERPRISE)
        a = rp.downgrade("app-1", PlanTier.GROWTH)
        assert a.tier == PlanTier.GROWTH

    def test_downgrade_higher_blocked(self):
        rp = AppApiRatePlan()
        rp.assign("app-1", PlanTier.FREE)
        with pytest.raises(ValueError, match="Cannot downgrade"):
            rp.downgrade("app-1", PlanTier.STARTER)
