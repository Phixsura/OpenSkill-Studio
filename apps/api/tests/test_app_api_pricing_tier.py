"""Tests for App API Pricing Tier — create, assign, feature check."""

import pytest

from app.services.app_api_pricing_tier import AppAPIPricingTier


class TestCreate:
    def test_create(self):
        p = AppAPIPricingTier()
        t = p.create_tier("inst-1", "pro", "Pro", 49.99, ["analytics", "webhooks", "sso"], rate_limit=5000)
        assert t.price_monthly == 49.99
        assert "sso" in t.features


class TestAssign:
    def test_assign_and_check(self):
        p = AppAPIPricingTier()
        p.create_tier("inst-1", "free", "Free", 0, ["basic_api"])
        p.create_tier("inst-1", "pro", "Pro", 49.99, ["basic_api", "webhooks"])
        p.assign_tier("inst-1", "tenant-1", "pro")
        assert p.has_feature("inst-1", "tenant-1", "webhooks") is True
        assert p.has_feature("inst-1", "tenant-1", "sso") is False

    def test_no_tier(self):
        p = AppAPIPricingTier()
        assert p.has_feature("inst-1", "nobody", "api") is False


class TestList:
    def test_sorted(self):
        p = AppAPIPricingTier()
        p.create_tier("inst-1", "pro", "Pro", 49.99, [], sort_order=2)
        p.create_tier("inst-1", "free", "Free", 0, [], sort_order=1)
        tiers = p.list_tiers("inst-1")
        assert tiers[0].name == "Free"


class TestIsolation:
    def test_cross(self):
        p = AppAPIPricingTier()
        p.create_tier("inst-1", "free", "Free", 0, [])
        assert p.list_tiers("inst-2") == []
