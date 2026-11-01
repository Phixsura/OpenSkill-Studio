"""Fleet AI Threat Intelligence — track AI security threat analysis."""
from __future__ import annotations
def fleet_ai_threat_intel(feeds: list[dict]) -> dict:
    active = [f for f in feeds if f.get("active", True)]
    indicators = sum(f.get("indicators", 0) for f in feeds)
    threats_24h = sum(f.get("threats_24h", 0) for f in feeds)
    mitigated = sum(f.get("mitigated", 0) for f in feeds)
    return {"feeds": len(feeds), "active": len(active), "indicators": indicators,
            "threats_24h": threats_24h, "mitigated": mitigated, "protected": mitigated >= threats_24h}
