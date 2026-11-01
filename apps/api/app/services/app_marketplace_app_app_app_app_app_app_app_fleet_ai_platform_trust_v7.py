"""Fleet AI Platform Trust v7 — track AI platform trust and transparency."""
from __future__ import annotations
def fleet_ai_platform_trust_v7(systems: list[dict]) -> dict:
    active = [s for s in systems if s.get("active", True)]
    trust_score = round(sum(s.get("score", 0) for s in systems) / max(len(systems), 1), 1)
    transparency_pct = round(sum(s.get("transparency", 0) for s in systems) / max(len(systems), 1), 1)
    certifications = set()
    for s in systems:
        certifications.update(s.get("certs", []))
    return {"systems": len(systems), "active": len(active), "score": trust_score,
            "transparency": transparency_pct, "certs": sorted(certifications), "trusted": trust_score > 90}
