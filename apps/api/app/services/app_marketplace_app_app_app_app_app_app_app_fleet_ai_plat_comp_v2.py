"""Fleet AI Platform Compliance v2 — track enterprise compliance requirements."""
from __future__ import annotations
def fleet_ai_platform_compliance_v2(frameworks: list[dict]) -> dict:
    active = [f for f in frameworks if f.get("active", True)]
    certifications = set()
    for f in frameworks:
        certifications.update(f.get("certs", []))
    controls = sum(f.get("controls", 0) for f in frameworks)
    compliance = round(sum(f.get("compliance_pct", 0) for f in frameworks) / max(len(frameworks), 1), 1)
    return {"frameworks": len(frameworks), "active": len(active), "certifications": sorted(certifications),
            "controls": controls, "compliance": compliance, "certified": len(certifications) > 3}
