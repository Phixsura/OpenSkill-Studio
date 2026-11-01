"""Fleet AI Long Context — track extended context window management."""
from __future__ import annotations
def fleet_ai_long_context(managers: list[dict]) -> dict:
    active = [m for m in managers if m.get("active", True)]
    max_tokens = max((m.get("max_tokens", 0) for m in managers), default=0)
    avg_utilization = round(sum(m.get("utilization_pct", 0) for m in managers) / max(len(managers), 1), 1)
    requests_24h = sum(m.get("requests_24h", 0) for m in managers)
    return {"managers": len(managers), "active": len(active), "max_tokens": max_tokens,
            "avg_utilization": avg_utilization, "requests_24h": requests_24h, "extended": max_tokens > 100000}
