"""Data pipeline — ETL pipeline step configuration."""

import html
from datetime import datetime, timezone

STEP_TYPES = {"extract": "📥", "transform": "🔄", "load": "📤", "validate": "✅", "filter": "🔍"}


def build_pipeline(*, steps: list[dict], name: str = "Pipeline") -> dict:
    items = []
    total_records = 0
    for i, s in enumerate(steps):
        stype = s.get("type", "transform")
        records = s.get("records_processed", 0)
        total_records += records
        items.append({
            "order": i + 1, "name": html.escape(s.get("name", f"Step {i+1}")),
            "type": stype, "icon": STEP_TYPES.get(stype, "⚙️"),
            "status": s.get("status", "pending"),
            "records_processed": records,
            "duration_ms": s.get("duration_ms", 0),
        })
    completed = sum(1 for s in items if s["status"] == "completed")
    return {"name": html.escape(name), "steps": items, "step_count": len(items),
            "completed": completed, "total_records": total_records,
            "progress_pct": round(completed / max(len(items), 1) * 100)}
