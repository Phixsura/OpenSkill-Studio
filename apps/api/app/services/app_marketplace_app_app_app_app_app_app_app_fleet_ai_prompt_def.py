"""Fleet AI Prompt Injection Defense — track prompt injection detection."""
from __future__ import annotations
def fleet_ai_prompt_defense(defenders: list[dict]) -> dict:
    active = [d for d in defenders if d.get("active", True)]
    scanned_24h = sum(d.get("scanned_24h", 0) for d in defenders)
    blocked_24h = sum(d.get("blocked_24h", 0) for d in defenders)
    false_positive_rate = round(sum(d.get("fp_rate", 0) for d in defenders) / max(len(defenders), 1), 2)
    return {"defenders": len(defenders), "active": len(active), "scanned_24h": scanned_24h,
            "blocked_24h": blocked_24h, "fp_rate": false_positive_rate, "secure": false_positive_rate < 1}
