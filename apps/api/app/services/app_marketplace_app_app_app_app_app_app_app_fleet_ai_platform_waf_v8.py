"""Fleet AI WAF v8 — track ultimate web application firewall."""
from __future__ import annotations
def fleet_ai_waf_v8(wafs: list[dict]) -> dict:
    active = [w for w in wafs if w.get("active", True)]
    rules = sum(w.get("rules", 0) for w in wafs)
    blocked = sum(w.get("blocked_24h", 0) for w in wafs)
    ml_rules = sum(w.get("ml_rules", 0) for w in wafs)
    return {"wafs": len(wafs), "active": len(active), "rules": rules,
            "blocked": blocked, "ml_rules": ml_rules, "ai_powered": ml_rules > 100}
