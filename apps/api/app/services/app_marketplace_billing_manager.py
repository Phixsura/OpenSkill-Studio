"""Billing Manager — handle extension pricing, subscriptions, and usage billing.

Supports free, one-time purchase, and subscription pricing models.
Tracks usage-based billing and generates invoices for extension developers.
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum


class PricingModel(str, Enum):
    FREE = "free"
    ONE_TIME = "one_time"
    SUBSCRIPTION = "subscription"
    USAGE_BASED = "usage_based"


class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    CANCELED = "canceled"
    PAST_DUE = "past_due"
    TRIAL = "trial"


@dataclass
class PricingPlan:
    plan_id: str
    extension_id: str
    model: PricingModel
    price_cents: int  # in cents, 0 for free
    currency: str = "USD"
    billing_period: str = "monthly"  # monthly, yearly, one_time
    trial_days: int = 0
    usage_unit: str = ""  # e.g. "api_call", "gb_storage"
    usage_price_cents: int = 0  # price per unit


class BillingManager:
    """Manages extension pricing and subscriptions."""

    def __init__(self):
        self._plans: dict[str, PricingPlan] = {}
        self._subscriptions: dict[str, dict] = {}  # sub_id -> sub record
        self._usage: dict[str, list[dict]] = {}  # sub_id -> usage records

    def create_plan(self, plan: PricingPlan) -> PricingPlan:
        self._plans[plan.plan_id] = plan
        return plan

    def get_plan(self, plan_id: str) -> PricingPlan | None:
        return self._plans.get(plan_id)

    def list_plans(self, extension_id: str) -> list[PricingPlan]:
        return [p for p in self._plans.values() if p.extension_id == extension_id]

    def subscribe(self, sub_id: str, org_id: str, plan_id: str) -> dict | None:
        plan = self._plans.get(plan_id)
        if not plan:
            return None
        now = datetime.now(timezone.utc).isoformat()
        status = SubscriptionStatus.TRIAL if plan.trial_days > 0 else SubscriptionStatus.ACTIVE
        sub = {
            "sub_id": sub_id, "org_id": org_id,
            "plan_id": plan_id, "extension_id": plan.extension_id,
            "status": status.value, "created_at": now,
            "amount_cents": plan.price_cents, "currency": plan.currency,
        }
        self._subscriptions[sub_id] = sub
        return sub

    def cancel_subscription(self, sub_id: str) -> bool:
        sub = self._subscriptions.get(sub_id)
        if sub and sub["status"] in (SubscriptionStatus.ACTIVE.value, SubscriptionStatus.TRIAL.value):
            sub["status"] = SubscriptionStatus.CANCELED.value
            sub["canceled_at"] = datetime.now(timezone.utc).isoformat()
            return True
        return False

    def get_subscription(self, sub_id: str) -> dict | None:
        return self._subscriptions.get(sub_id)

    def list_org_subscriptions(self, org_id: str) -> list[dict]:
        return [s for s in self._subscriptions.values() if s["org_id"] == org_id]

    def record_usage(self, sub_id: str, units: int, description: str = "") -> dict | None:
        sub = self._subscriptions.get(sub_id)
        if not sub or sub["status"] != SubscriptionStatus.ACTIVE.value:
            return None
        record = {
            "sub_id": sub_id, "units": units,
            "description": description,
            "recorded_at": datetime.now(timezone.utc).isoformat(),
        }
        self._usage.setdefault(sub_id, []).append(record)
        return record

    def get_usage_total(self, sub_id: str) -> int:
        return sum(r["units"] for r in self._usage.get(sub_id, []))

    def calculate_invoice(self, sub_id: str) -> dict | None:
        sub = self._subscriptions.get(sub_id)
        if not sub:
            return None
        plan = self._plans.get(sub["plan_id"])
        if not plan:
            return None
        base_amount = plan.price_cents
        usage_total = self.get_usage_total(sub_id)
        usage_amount = usage_total * plan.usage_price_cents
        return {
            "sub_id": sub_id, "base_amount_cents": base_amount,
            "usage_units": usage_total, "usage_amount_cents": usage_amount,
            "total_cents": base_amount + usage_amount,
            "currency": plan.currency,
        }
