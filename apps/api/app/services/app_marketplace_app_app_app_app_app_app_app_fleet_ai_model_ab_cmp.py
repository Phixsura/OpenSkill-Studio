"""Fleet AI Model A/B Compare — track side-by-side model output comparison."""
from __future__ import annotations
def fleet_ai_model_ab_compare(comparators: list[dict]) -> dict:
    active = [c for c in comparators if c.get("active", True)]
    comparisons_24h = sum(c.get("comparisons_24h", 0) for c in comparators)
    winners = sum(c.get("winners", 0) for c in comparators)
    ties = sum(c.get("ties", 0) for c in comparators)
    return {"comparators": len(comparators), "active": len(active), "comparisons_24h": comparisons_24h,
            "winners": winners, "ties": ties, "comparing": comparisons_24h > 0}
