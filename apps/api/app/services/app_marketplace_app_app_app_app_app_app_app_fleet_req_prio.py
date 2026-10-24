"""Fleet request priority — track priority queue distribution."""
from __future__ import annotations
def fleet_request_priority(requests: list[dict]) -> dict:
    by_prio: dict[str, int] = {}
    for r in requests:
        p = r.get("priority", "normal")
        by_prio[p] = by_prio.get(p, 0) + 1
    high = by_prio.get("high", 0) + by_prio.get("critical", 0)
    return {"total": len(requests), "by_priority": by_prio,
            "high_priority_pct": round(high / max(len(requests), 1) * 100, 1)}
