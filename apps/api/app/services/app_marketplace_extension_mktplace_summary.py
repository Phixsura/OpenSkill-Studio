"""Marketplace Summary — aggregate stats for the entire marketplace."""
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class MarketplaceSummary:
    total_extensions: int = 0
    total_developers: int = 0
    total_installs: int = 0
    total_reviews: int = 0
    avg_rating: float = 0.0
    categories: int = 0
    connectors: int = 0
    total_revenue_cents: int = 0


class MktplaceSummaryService:
    def __init__(self):
        self._summary = MarketplaceSummary()

    def update(self, **kwargs) -> MarketplaceSummary:
        for k, v in kwargs.items():
            if hasattr(self._summary, k):
                setattr(self._summary, k, v)
        return self._summary

    def increment(self, field: str, amount: int = 1) -> bool:
        if not hasattr(self._summary, field):
            return False
        current = getattr(self._summary, field)
        setattr(self._summary, field, current + amount)
        return True

    def get(self) -> MarketplaceSummary:
        return self._summary

    def get_highlights(self) -> dict:
        s = self._summary
        return {
            "extensions": s.total_extensions,
            "developers": s.total_developers,
            "installs": f"{s.total_installs:,}",
            "revenue": f"${s.total_revenue_cents / 100:,.2f}",
            "avg_rating": f"{s.avg_rating:.1f}/5.0",
        }
