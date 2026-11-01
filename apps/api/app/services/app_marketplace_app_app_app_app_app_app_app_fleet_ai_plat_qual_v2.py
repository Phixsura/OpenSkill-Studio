"""Fleet AI Platform Quality v2 — track platform-wide quality metrics."""
from __future__ import annotations
def fleet_ai_platform_quality_v2(monitors: list[dict]) -> dict:
    active = [m for m in monitors if m.get("active", True)]
    coverage = round(sum(m.get("coverage_pct", 0) for m in monitors) / max(len(monitors), 1), 1)
    bugs_open = sum(m.get("bugs_open", 0) for m in monitors)
    debt_hours = sum(m.get("debt_hours", 0) for m in monitors)
    return {"monitors": len(monitors), "active": len(active), "coverage": coverage,
            "bugs_open": bugs_open, "debt_hours": debt_hours, "quality": coverage > 80 and bugs_open < 50}
