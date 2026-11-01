"""Fleet request hedging — track hedged request effectiveness."""
from __future__ import annotations
def fleet_request_hedging(services: list[dict]) -> dict:
    total_hedged = sum(s.get("hedged_requests", 0) for s in services)
    saved_by_hedge = sum(s.get("saved_by_hedge", 0) for s in services)
    rate = round(saved_by_hedge / max(total_hedged, 1) * 100, 1)
    return {"total_hedged": total_hedged, "saved": saved_by_hedge, "effectiveness_pct": rate,
            "worthwhile": rate >= 10}
