"""API Usage Billing — metered billing for extension API consumption.

Tracks API call counts per endpoint, calculates costs based on tiered
pricing, generates invoices, and manages billing periods.
"""
from __future__ import annotations
import secrets
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class BillingPeriod(str, Enum):
    MONTHLY = "monthly"
    WEEKLY = "weekly"


@dataclass
class PricingTier:
    up_to: int  # 0 = unlimited
    price_per_call_cents: float  # e.g. 0.01 = $0.0001 per call


@dataclass
class UsageRecord:
    extension_id: str
    endpoint: str
    call_count: int = 0
    total_bytes: int = 0


@dataclass
class Invoice:
    invoice_id: str
    extension_id: str
    period_start: str
    period_end: str
    total_calls: int
    total_cost_cents: int
    line_items: list[dict] = field(default_factory=list)
    status: str = "pending"


DEFAULT_TIERS = [
    PricingTier(up_to=10000, price_per_call_cents=0.0),    # first 10k free
    PricingTier(up_to=100000, price_per_call_cents=0.01),  # $0.0001/call
    PricingTier(up_to=1000000, price_per_call_cents=0.005),# $0.00005/call
    PricingTier(up_to=0, price_per_call_cents=0.002),      # unlimited tier
]


class ApiUsageBillingService:
    """Tracks API usage and calculates metered billing."""

    def __init__(self, tiers: list[PricingTier] | None = None):
        self._usage: dict[str, dict[str, UsageRecord]] = defaultdict(dict)
        self._invoices: list[Invoice] = []
        self._tiers = tiers or DEFAULT_TIERS

    def record_usage(self, extension_id: str, endpoint: str,
                     calls: int = 1, bytes_transferred: int = 0) -> UsageRecord:
        if endpoint not in self._usage[extension_id]:
            self._usage[extension_id][endpoint] = UsageRecord(
                extension_id=extension_id, endpoint=endpoint)
        record = self._usage[extension_id][endpoint]
        record.call_count += calls
        record.total_bytes += bytes_transferred
        return record

    def get_usage(self, extension_id: str) -> dict:
        records = self._usage.get(extension_id, {})
        total_calls = sum(r.call_count for r in records.values())
        total_bytes = sum(r.total_bytes for r in records.values())
        return {
            "extension_id": extension_id,
            "total_calls": total_calls,
            "total_bytes": total_bytes,
            "endpoints": {ep: {"calls": r.call_count, "bytes": r.total_bytes}
                          for ep, r in records.items()},
        }

    def calculate_cost(self, total_calls: int) -> int:
        remaining = total_calls
        total_cost = 0.0
        for tier in self._tiers:
            if tier.up_to == 0:
                total_cost += remaining * tier.price_per_call_cents
                remaining = 0
                break
            tier_calls = min(remaining, tier.up_to)
            total_cost += tier_calls * tier.price_per_call_cents
            remaining -= tier_calls
            if remaining <= 0:
                break
        return int(total_cost)

    def generate_invoice(self, extension_id: str,
                         period_start: str, period_end: str) -> Invoice:
        usage = self.get_usage(extension_id)
        total_calls = usage["total_calls"]
        cost = self.calculate_cost(total_calls)

        line_items = []
        for ep, data in usage["endpoints"].items():
            line_items.append({
                "endpoint": ep, "calls": data["calls"],
                "bytes": data["bytes"],
            })

        invoice = Invoice(
            invoice_id=f"inv_{secrets.token_urlsafe(10)}",
            extension_id=extension_id,
            period_start=period_start, period_end=period_end,
            total_calls=total_calls, total_cost_cents=cost,
            line_items=line_items,
        )
        self._invoices.append(invoice)
        return invoice

    def reset_usage(self, extension_id: str) -> None:
        self._usage[extension_id] = {}

    def get_invoices(self, extension_id: str) -> list[Invoice]:
        return [i for i in self._invoices if i.extension_id == extension_id]
