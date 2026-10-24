"""Fleet WAF status — web application firewall metrics."""
from __future__ import annotations
def fleet_waf_status(rules: list[dict]) -> dict:
    blocked = sum(r.get("blocked", 0) for r in rules)
    allowed = sum(r.get("allowed", 0) for r in rules)
    return {"rules": len(rules), "blocked": blocked, "allowed": allowed,
            "block_rate_pct": round(blocked / max(blocked + allowed, 1) * 100, 2)}
