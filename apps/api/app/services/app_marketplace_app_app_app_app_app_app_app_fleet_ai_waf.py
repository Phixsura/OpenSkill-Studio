"""Fleet AI WAF — track web application firewall for AI endpoints."""
from __future__ import annotations
def fleet_ai_waf(wafs: list[dict]) -> dict:
    active = [w for w in wafs if w.get("active", True)]
    requests_24h = sum(w.get("requests_24h", 0) for w in wafs)
    blocked_24h = sum(w.get("blocked_24h", 0) for w in wafs)
    rules = sum(w.get("rules", 0) for w in wafs)
    return {"wafs": len(wafs), "active": len(active), "requests_24h": requests_24h,
            "blocked_24h": blocked_24h, "rules": rules, "protecting": blocked_24h >= 0}
