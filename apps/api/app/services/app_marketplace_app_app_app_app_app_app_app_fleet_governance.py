"""Fleet platform governance — track governance policy compliance."""
from __future__ import annotations
def fleet_governance(policies: list[dict]) -> dict:
    enforced = [p for p in policies if p.get("enforced", False)]
    audited = [p for p in policies if p.get("last_audit_days", 999) <= 90]
    return {"total": len(policies), "enforced": len(enforced), "audited": len(audited),
            "compliance_pct": round(len(enforced) / max(len(policies), 1) * 100, 1),
            "fully_governed": len(enforced) == len(policies)}
