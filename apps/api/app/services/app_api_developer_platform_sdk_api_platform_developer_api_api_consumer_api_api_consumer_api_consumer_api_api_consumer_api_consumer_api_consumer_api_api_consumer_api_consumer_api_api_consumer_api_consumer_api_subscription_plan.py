"""Consumer API Subscription Plan — manage subscription plans and upgrades."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import structlog

log = structlog.get_logger()

@dataclass
class SubscriptionPlan:
    plan_id: str
    name: str
    price_cents_monthly: int
    features: list[str] = field(default_factory=list)
    request_limit: int = 0
    rate_limit_rps: int = 0
    support_level: str = "community"

@dataclass
class Subscription:
    consumer_id: str
    plan_id: str
    status: str = "active"  # "active", "cancelled", "past_due", "trialing"
    started_at: datetime | None = None
    ends_at: datetime | None = None
    trial_ends_at: datetime | None = None

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiSubscriptionPlan:
    def __init__(self) -> None:
        self._plans: dict[tuple[str, str], SubscriptionPlan] = {}
        self._subscriptions: dict[tuple[str, str], Subscription] = {}

    def create_plan(self, installation_id: str, plan: SubscriptionPlan) -> SubscriptionPlan:
        if not installation_id:
            raise ValueError("installation_id is required")
        if plan.price_cents_monthly < 0:
            raise ValueError("Price must be non-negative")
        key = (installation_id, plan.plan_id)
        if key in self._plans:
            raise ValueError(f"Plan {plan.plan_id} already exists")
        self._plans[key] = plan
        return plan

    def subscribe(self, installation_id: str, consumer_id: str, plan_id: str, now: datetime, trial_days: int = 0) -> Subscription:
        if (installation_id, plan_id) not in self._plans:
            raise ValueError(f"Plan {plan_id} not found")
        sub = Subscription(consumer_id=consumer_id, plan_id=plan_id, status="trialing" if trial_days > 0 else "active", started_at=now, trial_ends_at=now + timedelta(days=trial_days) if trial_days > 0 else None)
        self._subscriptions[(installation_id, consumer_id)] = sub
        return sub

    def cancel(self, installation_id: str, consumer_id: str, now: datetime) -> Subscription:
        key = (installation_id, consumer_id)
        sub = self._subscriptions.get(key)
        if not sub:
            raise ValueError("Subscription not found")
        sub.status = "cancelled"
        sub.ends_at = now + timedelta(days=30)  # grace period
        return sub

    def upgrade(self, installation_id: str, consumer_id: str, new_plan_id: str) -> Subscription:
        if (installation_id, new_plan_id) not in self._plans:
            raise ValueError(f"Plan {new_plan_id} not found")
        key = (installation_id, consumer_id)
        sub = self._subscriptions.get(key)
        if not sub:
            raise ValueError("No active subscription")
        sub.plan_id = new_plan_id
        sub.status = "active"
        return sub

    def get_subscription(self, installation_id: str, consumer_id: str) -> Subscription | None:
        return self._subscriptions.get((installation_id, consumer_id))

    def list_plans(self, installation_id: str) -> list[SubscriptionPlan]:
        return sorted([p for (inst, _), p in self._plans.items() if inst == installation_id], key=lambda p: p.price_cents_monthly)
