"""Tests for App Rate Quota — tier definitions, usage checks, upgrades."""

import pytest

from app.services.app_rate_quota import AppRateQuota, TierQuota


@pytest.fixture
def quota():
    q = AppRateQuota()
    q.define_tier(TierQuota(tier="free", requests_per_day=100, requests_per_minute=10,
                             storage_mb=50, webhooks=5, priority=0))
    q.define_tier(TierQuota(tier="starter", requests_per_day=1000, requests_per_minute=60,
                             storage_mb=500, webhooks=20, priority=1))
    q.define_tier(TierQuota(tier="pro", requests_per_day=10000, requests_per_minute=300,
                             storage_mb=5000, webhooks=100, priority=2))
    return q


class TestDefineTier:
    def test_define(self, quota):
        t = quota.get_tier("free")
        assert t.requests_per_day == 100

    def test_missing_tier_name(self):
        q = AppRateQuota()
        with pytest.raises(ValueError):
            q.define_tier(TierQuota(tier="", requests_per_day=0, requests_per_minute=0,
                                   storage_mb=0, webhooks=0))

    def test_list_sorted(self, quota):
        tiers = quota.list_tiers()
        assert [t.tier for t in tiers] == ["free", "starter", "pro"]


class TestCheckUsage:
    def test_within_limit(self, quota):
        r = quota.check_usage("free", "requests_per_day", 50)
        assert r.exceeded is False
        assert r.remaining == 50

    def test_exceeded(self, quota):
        r = quota.check_usage("free", "requests_per_day", 150)
        assert r.exceeded is True
        assert r.overage == 50
        assert r.remaining == 0

    def test_at_limit(self, quota):
        r = quota.check_usage("free", "requests_per_day", 100)
        assert r.exceeded is False

    def test_unknown_metric(self, quota):
        with pytest.raises(ValueError, match="Unknown metric"):
            quota.check_usage("free", "bandwidth", 100)

    def test_unknown_tier(self, quota):
        with pytest.raises(KeyError):
            quota.check_usage("enterprise", "requests_per_day", 100)

    def test_storage_metric(self, quota):
        r = quota.check_usage("starter", "storage_mb", 300)
        assert r.exceeded is False
        assert r.remaining == 200


class TestRecommendUpgrade:
    def test_upgrade_recommendation(self, quota):
        rec = quota.recommend_upgrade("free", "requests_per_day", 500)
        assert rec == "starter"

    def test_needs_pro(self, quota):
        rec = quota.recommend_upgrade("free", "requests_per_day", 5000)
        assert rec == "pro"

    def test_no_upgrade_available(self, quota):
        rec = quota.recommend_upgrade("pro", "requests_per_day", 999999)
        assert rec is None

    def test_already_sufficient(self, quota):
        rec = quota.recommend_upgrade("starter", "requests_per_day", 500)
        assert rec is None  # starter already has 1000, no need for higher
