"""Fleet SLA penalty — track SLA breach penalties."""
from __future__ import annotations
def fleet_sla_penalty(breaches: list[dict]) -> dict:
    total_penalty = sum(b.get("penalty_usd", 0) for b in breaches)
    by_tier: dict[str, float] = {}
    for b in breaches:
        t = b.get("tier", "standard")
        by_tier[t] = by_tier.get(t, 0) + b.get("penalty_usd", 0)
    return {"breaches": len(breaches), "total_penalty_usd": round(total_penalty, 2),
            "by_tier": by_tier, "clean": len(breaches) == 0}
