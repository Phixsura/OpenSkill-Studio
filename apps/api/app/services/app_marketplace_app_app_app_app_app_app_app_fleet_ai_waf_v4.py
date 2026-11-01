"""Fleet AI WAF v4 — track advanced web application firewall for AI."""
from __future__ import annotations
def fleet_ai_waf_v4(wafs: list[dict]) -> dict:
    active = [w for w in wafs if w.get("active", True)]
    rules = sum(w.get("rules", 0) for w in wafs)
    blocked_24h = sum(w.get("blocked", 0) for w in wafs)
    ml_rules = sum(w.get("ml_rules", 0) for w in wafs)
    return {"wafs": len(wafs), "active": len(active), "rules": rules,
            "blocked": blocked_24h, "ml_rules": ml_rules, "ai_powered": ml_rules > 0}
