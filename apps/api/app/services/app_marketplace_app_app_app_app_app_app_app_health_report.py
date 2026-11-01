"""Platform health report — comprehensive health reporting."""
from __future__ import annotations
import time


def generate_report(services: list[dict], incidents: list[dict],
                     sla_compliance: float, uptime_pct: float) -> dict:
    healthy = sum(1 for s in services if s.get("status") == "healthy")
    degraded = sum(1 for s in services if s.get("status") == "degraded")
    down = len(services) - healthy - degraded
    open_incidents = sum(1 for i in incidents if i.get("status") == "open")
    score = round((healthy / max(len(services), 1)) * 50 + uptime_pct * 0.3 + sla_compliance * 0.2, 1)
    grade = "A" if score >= 95 else "B" if score >= 85 else "C" if score >= 70 else "D" if score >= 50 else "F"
    return {"generated_at": time.time(), "score": score, "grade": grade,
            "services": {"total": len(services), "healthy": healthy, "degraded": degraded, "down": down},
            "incidents": {"total": len(incidents), "open": open_incidents},
            "sla_compliance": sla_compliance, "uptime_pct": uptime_pct,
            "recommendation": "No action needed" if grade in ("A", "B") else "Review degraded services"}
