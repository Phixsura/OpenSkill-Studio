"""Offer management — structured offer letters, negotiation, acceptance tracking.

Features:
  - Offer letter templates per org
  - Offer creation with compensation, start date, conditions
  - Counter-offer workflow
  - Offer expiration tracking
  - Acceptance/decline with reason
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

OFFER_STATUSES = frozenset({
    "draft", "sent", "viewed", "countered",
    "accepted", "declined", "expired", "withdrawn",
})

OFFER_TRANSITIONS: dict[str, set[str]] = {
    "draft": {"sent", "withdrawn"},
    "sent": {"viewed", "accepted", "declined", "countered", "expired", "withdrawn"},
    "viewed": {"accepted", "declined", "countered", "expired", "withdrawn"},
    "countered": {"sent", "accepted", "declined", "withdrawn"},
    "accepted": set(),
    "declined": set(),
    "expired": set(),
    "withdrawn": set(),
}


@dataclass(frozen=True, slots=True)
class OfferTemplate:
    """Reusable offer letter template."""
    name: str
    sections: list[dict]  # [{title, content_template}]
    default_conditions: list[str]
    default_expiry_days: int


@dataclass(frozen=True, slots=True)
class OfferSummary:
    """Offer analytics summary."""
    total_offers: int
    acceptance_rate: float
    avg_time_to_decision_days: float | None
    avg_negotiation_rounds: float
    offers_by_status: dict[str, int]


class OfferManagementService:
    def __init__(self, db: AsyncSession):
        self.db = db

    def validate_transition(self, current: str, target: str) -> bool:
        """Execute validate transition."""
        return target in OFFER_TRANSITIONS.get(current, set())

    def create_offer_data(
        self,
        *,
        application_id: str,
        role_title: str,
        compensation_text: str | None = None,
        start_date: datetime | None = None,
        conditions: list[str] | None = None,
        expiry_days: int = 7,
        custom_sections: list[dict] | None = None,
    ) -> dict:
        """Build structured offer data (stored in Application or Placement metadata)."""
        return {
            "application_id": application_id,
            "role_title": role_title,
            "compensation_text": compensation_text,
            "start_date": start_date.isoformat() if start_date else None,
            "conditions": conditions or [],
            "custom_sections": custom_sections or [],
            "expires_at": (datetime.now(UTC) + timedelta(days=expiry_days)).isoformat(),
            "created_at": datetime.now(UTC).isoformat(),
            "status": "draft",
            "negotiation_history": [],
        }

    def add_counter_offer(self, offer_data: dict, counter: dict) -> dict:
        """Add a counter-offer to negotiation history."""
        offer_data["negotiation_history"].append({
            "type": "counter",
            "details": counter,
            "timestamp": datetime.now(UTC).isoformat(),
        })
        offer_data["status"] = "countered"
        return offer_data

    def compute_offer_analytics(self, offers: list[dict]) -> OfferSummary:
        """Compute analytics from a list of offer records."""
        if not offers:
            return OfferSummary(0, 0.0, None, 0.0, {})

        by_status: dict[str, int] = {}
        decision_days: list[float] = []
        negotiation_rounds: list[int] = []

        for o in offers:
            status = o.get("status", "unknown")
            by_status[status] = by_status.get(status, 0) + 1
            negotiation_rounds.append(len(o.get("negotiation_history", [])))

        accepted = by_status.get("accepted", 0)
        total_decided = accepted + by_status.get("declined", 0)
        rate = accepted / total_decided if total_decided > 0 else 0.0

        return OfferSummary(
            total_offers=len(offers),
            acceptance_rate=round(rate, 3),
            avg_time_to_decision_days=round(sum(decision_days) / len(decision_days), 1) if decision_days else None,
            avg_negotiation_rounds=round(sum(negotiation_rounds) / len(negotiation_rounds), 2) if negotiation_rounds else 0.0,
            offers_by_status=by_status,
        )
