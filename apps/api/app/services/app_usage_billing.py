"""App Usage Billing — compute billing line items from metered usage.

Translates raw usage metrics into billable amounts:
- Tiered pricing: included quota + overage rates
- Per-metric billing: API calls, bandwidth, storage, compute, webhooks
- Billing period aggregation (monthly)
- Invoice line item generation
- Credit/discount application
- Billing summary with totals
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum

import structlog

log = structlog.get_logger()


class BillableMetric(str, Enum):
    API_CALLS = "api_calls"
    BANDWIDTH_GB = "bandwidth_gb"
    STORAGE_GB = "storage_gb"
    COMPUTE_HOURS = "compute_hours"
    WEBHOOK_DELIVERIES = "webhook_deliveries"


@dataclass(frozen=True)
class PricingTier:
    """Pricing for a single metric."""

    included_qty: int         # free/included in base plan
    overage_rate: float       # cost per unit above included
    unit_label: str           # e.g. "per 1K calls", "per GB"


@dataclass
class UsageEntry:
    """Raw usage for billing."""

    app_id: str
    metric: BillableMetric
    quantity: float
    period: str               # "2026-10"


@dataclass
class LineItem:
    """A billing line item."""

    metric: BillableMetric
    description: str
    quantity: float
    included: float
    overage: float
    unit_rate: float
    amount: float             # overage * unit_rate


@dataclass
class BillingSummary:
    """Complete billing summary for a period."""

    app_id: str
    period: str
    line_items: list[LineItem]
    subtotal: float
    credits: float
    total: float


# Default pricing
DEFAULT_PRICING: dict[BillableMetric, PricingTier] = {
    BillableMetric.API_CALLS: PricingTier(50_000, 0.001, "per call"),
    BillableMetric.BANDWIDTH_GB: PricingTier(10, 0.10, "per GB"),
    BillableMetric.STORAGE_GB: PricingTier(5, 0.05, "per GB"),
    BillableMetric.COMPUTE_HOURS: PricingTier(10, 0.50, "per hour"),
    BillableMetric.WEBHOOK_DELIVERIES: PricingTier(10_000, 0.0005, "per delivery"),
}


class AppUsageBilling:
    """Compute billing from usage metrics."""

    def __init__(self, pricing: dict[BillableMetric, PricingTier] | None = None):
        self._pricing = pricing or dict(DEFAULT_PRICING)
        # (app_id, period, metric) → quantity
        self._usage: dict[tuple[str, str, BillableMetric], float] = {}
        # app_id → credits balance
        self._credits: dict[str, float] = {}

    def record_usage(self, entry: UsageEntry) -> None:
        """Record usage for billing."""
        if entry.quantity < 0:
            raise ValueError("Usage quantity must be non-negative")
        key = (entry.app_id, entry.period, entry.metric)
        self._usage[key] = self._usage.get(key, 0) + entry.quantity

    def add_credit(self, app_id: str, amount: float) -> float:
        """Add billing credit. Returns new balance."""
        if amount <= 0:
            raise ValueError("Credit amount must be positive")
        self._credits[app_id] = self._credits.get(app_id, 0) + amount
        return self._credits[app_id]

    def get_credit_balance(self, app_id: str) -> float:
        return self._credits.get(app_id, 0)

    def compute_bill(self, app_id: str, period: str) -> BillingSummary:
        """Compute the billing summary for an app and period."""
        line_items: list[LineItem] = []

        for metric, tier in self._pricing.items():
            key = (app_id, period, metric)
            quantity = self._usage.get(key, 0)
            overage = max(0, quantity - tier.included_qty)
            amount = round(overage * tier.overage_rate, 4)

            line_items.append(LineItem(
                metric=metric,
                description=f"{metric.value} ({tier.unit_label})",
                quantity=quantity,
                included=min(quantity, tier.included_qty),
                overage=overage,
                unit_rate=tier.overage_rate,
                amount=amount,
            ))

        subtotal = round(sum(li.amount for li in line_items), 2)

        # Apply credits
        credit_balance = self._credits.get(app_id, 0)
        credits_applied = min(credit_balance, subtotal)
        total = round(max(0, subtotal - credits_applied), 2)

        if credits_applied > 0:
            self._credits[app_id] = round(credit_balance - credits_applied, 2)

        return BillingSummary(
            app_id=app_id,
            period=period,
            line_items=line_items,
            subtotal=subtotal,
            credits=credits_applied,
            total=total,
        )

    def get_usage(self, app_id: str, period: str, metric: BillableMetric) -> float:
        return self._usage.get((app_id, period, metric), 0)

    def estimate_cost(self, metric: BillableMetric, quantity: float) -> float:
        """Estimate cost for a given quantity (for projections)."""
        tier = self._pricing.get(metric)
        if tier is None:
            return 0.0
        overage = max(0, quantity - tier.included_qty)
        return round(overage * tier.overage_rate, 4)
