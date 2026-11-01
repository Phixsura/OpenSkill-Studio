"""SLO dashboard — unified view of all service level objectives."""
from __future__ import annotations


def slo_dashboard(slos: list[dict]) -> dict:
    meeting = sum(1 for s in slos if s.get("current", 0) >= s.get("target", 0))
    at_risk = sum(1 for s in slos if s.get("current", 0) < s.get("target", 0) and
                  s.get("current", 0) >= s.get("target", 0) * 0.99)
    breaching = sum(1 for s in slos if s.get("current", 0) < s.get("target", 0) * 0.99)
    return {"total": len(slos), "meeting": meeting, "at_risk": at_risk,
            "breaching": breaching,
            "overall_health": "green" if breaching == 0 and at_risk == 0 else (
                "yellow" if breaching == 0 else "red")}
