"""Fleet admission controller — track webhook admission decisions."""
from __future__ import annotations
def fleet_admission_stats(webhooks: list[dict]) -> dict:
    total_calls = sum(w.get("calls", 0) for w in webhooks)
    denied = sum(w.get("denied", 0) for w in webhooks)
    errors = sum(w.get("errors", 0) for w in webhooks)
    return {"webhooks": len(webhooks), "total_calls": total_calls,
            "denied": denied, "errors": errors, "healthy": errors == 0}
