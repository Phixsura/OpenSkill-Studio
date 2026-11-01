"""Tests for Consumer Billing Meter service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_billing_meter import (
    BillingMeter, BillingPlan, PricingTier,
)


class TestBillingMeter:
    def test_flat_rate_billing(self):
        svc = BillingMeter()
        svc.create_plan(BillingPlan("basic", "Basic", base_price_cents=2999))
        svc.assign_plan("c1", "basic")
        svc.record_usage("c1", "2024-01", 500)
        bill = svc.calculate_bill("c1", "2024-01")
        assert bill["total_cents"] == 2999
        assert bill["total_dollars"] == 29.99

    def test_tiered_billing(self):
        svc = BillingMeter()
        plan = BillingPlan("usage", "Usage", base_price_cents=0, tiers=[
            PricingTier(up_to=100, unit_price_cents=10),
            PricingTier(up_to=None, unit_price_cents=5),
        ])
        svc.create_plan(plan)
        svc.assign_plan("c1", "usage")
        svc.record_usage("c1", "2024-01", 250)
        bill = svc.calculate_bill("c1", "2024-01")
        # 100 * 10 + 150 * 5 = 1000 + 750 = 1750
        assert bill["usage_price_cents"] == 1750
        assert bill["total_cents"] == 1750

    def test_included_units(self):
        svc = BillingMeter()
        plan = BillingPlan("pro", "Pro", base_price_cents=4999, included_units=1000,
                           tiers=[PricingTier(up_to=None, unit_price_cents=2)])
        svc.create_plan(plan)
        svc.assign_plan("c1", "pro")
        svc.record_usage("c1", "2024-01", 1500)
        bill = svc.calculate_bill("c1", "2024-01")
        assert bill["billable_units"] == 500
        assert bill["usage_price_cents"] == 1000
        assert bill["total_cents"] == 5999

    def test_within_included(self):
        svc = BillingMeter()
        plan = BillingPlan("free", "Free", base_price_cents=0, included_units=100)
        svc.create_plan(plan)
        svc.assign_plan("c1", "free")
        svc.record_usage("c1", "2024-01", 50)
        bill = svc.calculate_bill("c1", "2024-01")
        assert bill["total_cents"] == 0

    def test_accumulate_usage(self):
        svc = BillingMeter()
        svc.create_plan(BillingPlan("p", "P"))
        svc.assign_plan("c1", "p")
        svc.record_usage("c1", "2024-01", 100)
        svc.record_usage("c1", "2024-01", 50)
        summary = svc.get_usage_summary("c1")
        assert summary["by_period"]["2024-01"] == 150

    def test_no_plan_assigned(self):
        svc = BillingMeter()
        assert svc.calculate_bill("c1", "2024-01")["error"] == "no_plan_assigned"

    def test_negative_units(self):
        svc = BillingMeter()
        with pytest.raises(ValueError):
            svc.record_usage("c1", "2024-01", -5)

    def test_duplicate_plan(self):
        svc = BillingMeter()
        svc.create_plan(BillingPlan("p1", "P1"))
        with pytest.raises(ValueError):
            svc.create_plan(BillingPlan("p1", "P2"))

    def test_list_plans(self):
        svc = BillingMeter()
        svc.create_plan(BillingPlan("a", "A"))
        svc.create_plan(BillingPlan("b", "B"))
        assert len(svc.list_plans()) == 2

    def test_isolation(self):
        a, b = BillingMeter(), BillingMeter()
        a.create_plan(BillingPlan("p1", "P1"))
        assert b.list_plans() == []
