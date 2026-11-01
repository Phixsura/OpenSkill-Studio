"""Fleet AI Input Sanitizer — track AI input cleaning and normalization."""
from __future__ import annotations
def fleet_ai_input_sanitizer(sanitizers: list[dict]) -> dict:
    active = [s for s in sanitizers if s.get("active", True)]
    sanitized_24h = sum(s.get("sanitized_24h", 0) for s in sanitizers)
    threats_blocked = sum(s.get("threats", 0) for s in sanitizers)
    rules = sum(s.get("rules", 0) for s in sanitizers)
    return {"sanitizers": len(sanitizers), "active": len(active), "sanitized_24h": sanitized_24h,
            "threats": threats_blocked, "rules": rules, "protecting": threats_blocked >= 0}
