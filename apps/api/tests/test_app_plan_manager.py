"""Tests for App Plan Manager — plans, features, assignment, comparison."""

import pytest

from app.services.app_plan_manager import AppPlanManager


@pytest.fixture
def pm():
    m = AppPlanManager()
    m.define_plan("free", "Free", ["basic_api"], price_cents=0, tier=0)
    m.define_plan("pro", "Pro", ["basic_api", "webhooks", "analytics"], price_cents=2900, tier=1)
    m.define_plan("enterprise", "Enterprise", ["basic_api", "webhooks", "analytics", "sso", "sla"], price_cents=9900, tier=2)
    return m


class TestDefinePlan:
    def test_define(self, pm):
        plans = pm.list_plans()
        assert len(plans) == 3
        assert plans[0].plan_id == "free"

    def test_missing_id(self):
        m = AppPlanManager()
        with pytest.raises(ValueError):
            m.define_plan("", "X", [])


class TestAssignment:
    def test_assign(self, pm):
        pm.assign_plan("inst-1", "pro")
        plan = pm.get_plan("inst-1")
        assert plan is not None
        assert plan.plan_id == "pro"

    def test_unknown_plan(self, pm):
        with pytest.raises(KeyError):
            pm.assign_plan("inst-1", "nonexistent")

    def test_no_assignment(self, pm):
        assert pm.get_plan("inst-1") is None


class TestFeatureAccess:
    def test_has_feature(self, pm):
        pm.assign_plan("inst-1", "pro")
        assert pm.has_feature("inst-1", "webhooks") is True
        assert pm.has_feature("inst-1", "sso") is False

    def test_no_plan_no_features(self, pm):
        assert pm.has_feature("inst-1", "basic_api") is False


class TestComparePlans:
    def test_compare(self, pm):
        diff = pm.compare_plans("free", "pro")
        assert "webhooks" in diff["only_in_b"]
        assert "basic_api" in diff["shared"]
        assert diff["only_in_a"] == []

    def test_compare_unknown(self, pm):
        with pytest.raises(KeyError):
            pm.compare_plans("free", "nope")


class TestUpgradeOptions:
    def test_upgrades(self, pm):
        pm.assign_plan("inst-1", "free")
        options = pm.get_upgrade_options("inst-1")
        assert [o.plan_id for o in options] == ["pro", "enterprise"]

    def test_no_plan_all_options(self, pm):
        options = pm.get_upgrade_options("inst-1")
        assert len(options) == 3

    def test_top_tier_no_upgrades(self, pm):
        pm.assign_plan("inst-1", "enterprise")
        assert pm.get_upgrade_options("inst-1") == []


class TestListPlans:
    def test_sorted_by_tier(self, pm):
        plans = pm.list_plans()
        assert [p.tier for p in plans] == [0, 1, 2]
