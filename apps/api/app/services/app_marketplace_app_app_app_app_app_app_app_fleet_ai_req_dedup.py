"""Fleet AI Request Dedup — track duplicate AI request elimination."""
from __future__ import annotations
def fleet_ai_request_dedup(dedupers: list[dict]) -> dict:
    active = [d for d in dedupers if d.get("active", True)]
    requests_24h = sum(d.get("requests_24h", 0) for d in dedupers)
    deduped = sum(d.get("deduped", 0) for d in dedupers)
    savings_pct = round(deduped / max(requests_24h, 1) * 100, 1)
    return {"dedupers": len(dedupers), "active": len(active), "requests_24h": requests_24h,
            "deduped": deduped, "savings_pct": savings_pct, "saving": savings_pct > 5}
