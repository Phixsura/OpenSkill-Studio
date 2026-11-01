"""Fleet Auto Remediation v9 — track automated incident remediation."""
from __future__ import annotations
def fleet_auto_remediation_v9(rules: list[dict]) -> dict:
    active = [r for r in rules if r.get("active")]
    triggered = sum(r.get("triggered_today", 0) for r in rules)
    success = sum(r.get("success_today", 0) for r in rules)
    return {"rules": len(rules), "active": len(active), "triggered_today": triggered,
            "success_today": success, "healthy": success >= triggered * 0.9 if triggered else True}
