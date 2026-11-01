"""Tests for App Usage Billing — line items, overage, credits, estimates."""

import pytest

from app.services.app_usage_billing import (
    AppUsageBilling,
    BillableMetric,
    UsageEntry,
)


class TestRecordUsage:
    def test_record_and_get(self):
        b = AppUsageBilling()
        b.record_usage(UsageEntry("app-1", BillableMetric.API_CALLS, 30000, "2026-10"))
        assert b.get_usage("app-1", "2026-10", BillableMetric.API_CALLS) == 30000

    def test_accumulates(self):
        b = AppUsageBilling()
        b.record_usage(UsageEntry("app-1", BillableMetric.API_CALLS, 10000, "2026-10"))
        b.record_usage(UsageEntry("app-1", BillableMetric.API_CALLS, 20000, "2026-10"))
        assert b.get_usage("app-1", "2026-10", BillableMetric.API_CALLS) == 30000

    def test_negative_rejected(self):
        b = AppUsageBilling()
        with pytest.raises(ValueError, match="non-negative"):
            b.record_usage(UsageEntry("app-1", BillableMetric.API_CALLS, -100, "2026-10"))

    def test_zero_usage(self):
        b = AppUsageBilling()
        assert b.get_usage("app-1", "2026-10", BillableMetric.API_CALLS) == 0


class TestBilling:
    def test_within_included_no_charge(self):
        b = AppUsageBilling()
        b.record_usage(UsageEntry("app-1", BillableMetric.API_CALLS, 30000, "2026-10"))
        bill = b.compute_bill("app-1", "2026-10")
        api_item = [li for li in bill.line_items if li.metric == BillableMetric.API_CALLS][0]
        assert api_item.overage == 0
        assert api_item.amount == 0
        assert bill.total == 0

    def test_overage_charged(self):
        b = AppUsageBilling()
        # Default: 50K included, $0.001/call overage
        b.record_usage(UsageEntry("app-1", BillableMetric.API_CALLS, 60000, "2026-10"))
        bill = b.compute_bill("app-1", "2026-10")
        api_item = [li for li in bill.line_items if li.metric == BillableMetric.API_CALLS][0]
        assert api_item.overage == 10000
        assert api_item.amount == pytest.approx(10.0)  # 10000 * 0.001
        assert bill.subtotal >= 10.0

    def test_multiple_metrics(self):
        b = AppUsageBilling()
        b.record_usage(UsageEntry("app-1", BillableMetric.API_CALLS, 60000, "2026-10"))
        b.record_usage(UsageEntry("app-1", BillableMetric.BANDWIDTH_GB, 15, "2026-10"))
        bill = b.compute_bill("app-1", "2026-10")
        bw = [li for li in bill.line_items if li.metric == BillableMetric.BANDWIDTH_GB][0]
        assert bw.overage == 5  # 15 - 10 included
        assert bw.amount == pytest.approx(0.5)  # 5 * 0.10
        assert bill.subtotal >= 10.5

    def test_all_metrics_in_bill(self):
        b = AppUsageBilling()
        bill = b.compute_bill("app-1", "2026-10")
        metrics = {li.metric for li in bill.line_items}
        for m in BillableMetric:
            assert m in metrics

    def test_line_item_details(self):
        b = AppUsageBilling()
        b.record_usage(UsageEntry("app-1", BillableMetric.STORAGE_GB, 8, "2026-10"))
        bill = b.compute_bill("app-1", "2026-10")
        storage = [li for li in bill.line_items if li.metric == BillableMetric.STORAGE_GB][0]
        assert storage.quantity == 8
        assert storage.included == 5
        assert storage.overage == 3
        assert storage.unit_rate == 0.05
        assert storage.amount == pytest.approx(0.15)

    def test_no_usage_zero_bill(self):
        b = AppUsageBilling()
        bill = b.compute_bill("app-1", "2026-10")
        assert bill.total == 0
        assert bill.subtotal == 0


class TestCredits:
    def test_add_credit(self):
        b = AppUsageBilling()
        balance = b.add_credit("app-1", 50.0)
        assert balance == 50.0
        assert b.get_credit_balance("app-1") == 50.0

    def test_credits_reduce_total(self):
        b = AppUsageBilling()
        b.record_usage(UsageEntry("app-1", BillableMetric.API_CALLS, 60000, "2026-10"))
        b.add_credit("app-1", 5.0)
        bill = b.compute_bill("app-1", "2026-10")
        assert bill.credits == 5.0
        assert bill.total == pytest.approx(bill.subtotal - 5.0)

    def test_credits_cannot_go_negative_total(self):
        b = AppUsageBilling()
        b.record_usage(UsageEntry("app-1", BillableMetric.API_CALLS, 51000, "2026-10"))
        b.add_credit("app-1", 100.0)  # more than enough
        bill = b.compute_bill("app-1", "2026-10")
        assert bill.total == 0
        # Remaining credits preserved
        assert b.get_credit_balance("app-1") > 0

    def test_credits_consumed(self):
        b = AppUsageBilling()
        b.record_usage(UsageEntry("app-1", BillableMetric.API_CALLS, 60000, "2026-10"))
        b.add_credit("app-1", 3.0)
        bill = b.compute_bill("app-1", "2026-10")
        assert bill.credits == 3.0
        assert b.get_credit_balance("app-1") == 0  # fully used

    def test_add_credit_negative_rejected(self):
        b = AppUsageBilling()
        with pytest.raises(ValueError, match="positive"):
            b.add_credit("app-1", -10)

    def test_no_credits_balance(self):
        b = AppUsageBilling()
        assert b.get_credit_balance("unknown") == 0


class TestEstimate:
    def test_estimate_within_included(self):
        b = AppUsageBilling()
        cost = b.estimate_cost(BillableMetric.API_CALLS, 30000)
        assert cost == 0

    def test_estimate_overage(self):
        b = AppUsageBilling()
        cost = b.estimate_cost(BillableMetric.API_CALLS, 60000)
        assert cost == pytest.approx(10.0)

    def test_estimate_compute(self):
        b = AppUsageBilling()
        cost = b.estimate_cost(BillableMetric.COMPUTE_HOURS, 20)
        assert cost == pytest.approx(5.0)  # 10 overage * $0.50
