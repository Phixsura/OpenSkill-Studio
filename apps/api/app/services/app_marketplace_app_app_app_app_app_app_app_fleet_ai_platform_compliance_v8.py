"""Fleet AI Compliance v8 — track ultimate regulatory compliance."""
from __future__ import annotations
def fleet_ai_compliance_v8(frameworks: list[dict]) -> dict:
    active = [f for f in frameworks if f.get("active", True)]
    certs = set()
    for f in frameworks:
        certs.update(f.get("certs", []))
    controls = sum(f.get("controls", 0) for f in frameworks)
    compliance = round(sum(f.get("pct", 0) for f in frameworks) / max(len(frameworks), 1), 1)
    return {"frameworks": len(frameworks), "active": len(active), "certs": sorted(certs),
            "controls": controls, "compliance": compliance, "certified": compliance > 99}
