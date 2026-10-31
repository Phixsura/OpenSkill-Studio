"""Fleet AI Context Window Manager — track context window optimization."""
from __future__ import annotations
def fleet_ai_context_window(managers: list[dict]) -> dict:
    active = [m for m in managers if m.get("active", True)]
    max_tokens = max((m.get("max_tokens", 0) for m in managers), default=0)
    avg_usage_pct = round(sum(m.get("usage_pct", 0) for m in managers) / max(len(managers), 1), 1)
    overflows_24h = sum(m.get("overflows", 0) for m in managers)
    return {"managers": len(managers), "active": len(active), "max_tokens": max_tokens,
            "usage_pct": avg_usage_pct, "overflows": overflows_24h, "optimized": overflows_24h == 0}
