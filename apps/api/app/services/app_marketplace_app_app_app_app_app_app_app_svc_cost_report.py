"""Service cost report — generate per-service cost breakdown."""
from __future__ import annotations


def generate_cost_report(services: list[dict]) -> dict:
    total = sum(s.get("monthly_cost", 0) for s in services)
    report = []
    for s in sorted(services, key=lambda x: -x.get("monthly_cost", 0)):
        share = round(s.get("monthly_cost", 0) / max(total, 0.01) * 100, 1)
        report.append({"service": s["name"], "cost": s["monthly_cost"],
                        "share_pct": share, "team": s.get("team", "")})
    return {"services": report, "total_cost": round(total, 2), "service_count": len(report)}
