"""Subscription Lifecycle — manage extension subscription state transitions.

Handles the complete subscription lifecycle: trial → active → renewal →
cancellation → grace period → expiration, with proration and dunning.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class SubState(str, Enum):
    TRIAL = "trial"
    ACTIVE = "active"
    PAST_DUE = "past_due"
    GRACE_PERIOD = "grace_period"
    CANCELED = "canceled"
    EXPIRED = "expired"


VALID_TRANSITIONS: dict[SubState, list[SubState]] = {
    SubState.TRIAL: [SubState.ACTIVE, SubState.CANCELED, SubState.EXPIRED],
    SubState.ACTIVE: [SubState.PAST_DUE, SubState.CANCELED],
    SubState.PAST_DUE: [SubState.ACTIVE, SubState.GRACE_PERIOD, SubState.CANCELED],
    SubState.GRACE_PERIOD: [SubState.ACTIVE, SubState.EXPIRED],
    SubState.CANCELED: [SubState.ACTIVE],  # reactivation
    SubState.EXPIRED: [],
}


@dataclass
class Subscription:
    sub_id: str
    org_id: str
    extension_id: str
    plan_id: str
    state: SubState
    amount_cents: int
    created_at: str = ""
    state_history: list[dict] = field(default_factory=list)
    dunning_attempts: int = 0
    cancel_reason: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()


class SubscriptionLifecycleService:
    """Manages subscription state transitions with business rules."""

    def __init__(self, max_dunning_attempts: int = 3, grace_period_days: int = 7):
        self._subs: dict[str, Subscription] = {}
        self._max_dunning = max_dunning_attempts
        self._grace_days = grace_period_days

    def create(self, sub_id: str, org_id: str, extension_id: str,
               plan_id: str, amount_cents: int, trial: bool = False) -> Subscription:
        state = SubState.TRIAL if trial else SubState.ACTIVE
        sub = Subscription(sub_id=sub_id, org_id=org_id, extension_id=extension_id,
                           plan_id=plan_id, state=state, amount_cents=amount_cents)
        sub.state_history.append({"state": state.value, "at": sub.created_at})
        self._subs[sub_id] = sub
        return sub

    def transition(self, sub_id: str, target: SubState, reason: str = "") -> tuple[bool, str]:
        sub = self._subs.get(sub_id)
        if not sub:
            return False, "Subscription not found"
        allowed = VALID_TRANSITIONS.get(sub.state, [])
        if target not in allowed:
            return False, f"Cannot transition from {sub.state.value} to {target.value}"
        now = datetime.now(timezone.utc).isoformat()
        sub.state = target
        sub.state_history.append({"state": target.value, "at": now, "reason": reason})
        if target == SubState.CANCELED:
            sub.cancel_reason = reason
        return True, f"Transitioned to {target.value}"

    def record_payment_failure(self, sub_id: str) -> tuple[SubState, str]:
        """Handle a payment failure with dunning logic."""
        sub = self._subs.get(sub_id)
        if not sub:
            return SubState.EXPIRED, "Not found"
        sub.dunning_attempts += 1
        if sub.state == SubState.ACTIVE:
            self.transition(sub_id, SubState.PAST_DUE, "Payment failed")
        if sub.dunning_attempts >= self._max_dunning:
            self.transition(sub_id, SubState.GRACE_PERIOD, "Max dunning attempts reached")
        return sub.state, f"Dunning attempt {sub.dunning_attempts}"

    def record_payment_success(self, sub_id: str) -> bool:
        sub = self._subs.get(sub_id)
        if not sub:
            return False
        if sub.state in (SubState.PAST_DUE, SubState.GRACE_PERIOD, SubState.CANCELED):
            self.transition(sub_id, SubState.ACTIVE, "Payment received")
            sub.dunning_attempts = 0
            return True
        return False

    def get(self, sub_id: str) -> Subscription | None:
        return self._subs.get(sub_id)

    def list_by_org(self, org_id: str, state: SubState | None = None) -> list[Subscription]:
        subs = [s for s in self._subs.values() if s.org_id == org_id]
        if state:
            subs = [s for s in subs if s.state == state]
        return subs

    def get_mrr(self) -> int:
        """Get total Monthly Recurring Revenue in cents."""
        return sum(s.amount_cents for s in self._subs.values()
                   if s.state in (SubState.ACTIVE, SubState.TRIAL, SubState.PAST_DUE))
