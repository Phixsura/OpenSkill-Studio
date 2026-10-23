"""Migration planner — database migration step builder."""

import html
from datetime import datetime, timezone


def build_migration_plan(*, steps: list[dict]) -> dict:
    items = []
    total_risk = 0
    for i, s in enumerate(steps):
        risk = s.get("risk", "low")
        risk_score = {"low": 1, "medium": 2, "high": 3, "critical": 4}.get(risk, 1)
        total_risk += risk_score
        items.append({
            "order": i + 1,
            "name": html.escape(s.get("name", f"Step {i+1}")),
            "description": html.escape(s.get("description", "")),
            "type": s.get("type", "schema"),
            "risk": risk,
            "risk_score": risk_score,
            "reversible": s.get("reversible", True),
            "estimated_seconds": s.get("estimated_seconds", 0),
        })
    avg_risk = round(total_risk / max(len(items), 1), 1)
    total_time = sum(i["estimated_seconds"] for i in items)
    has_irreversible = any(not i["reversible"] for i in items)
    return {"steps": items, "total_steps": len(items), "avg_risk_score": avg_risk,
            "total_estimated_seconds": total_time, "has_irreversible": has_irreversible,
            "created_at": datetime.now(timezone.utc).isoformat()}
