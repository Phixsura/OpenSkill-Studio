"""Deployment pipeline — CI/CD stage tracking."""

import html
from datetime import datetime, timezone

STAGE_ICONS = {"build": "🔨", "test": "🧪", "lint": "🔍", "deploy": "🚀", "verify": "✅"}


def build_pipeline(*, stages: list[dict], pipeline_id: str = "") -> dict:
    items = []
    overall = "success"
    total_duration = 0
    for s in stages:
        status = s.get("status", "pending")
        dur = s.get("duration_s", 0)
        total_duration += dur
        if status == "failed":
            overall = "failed"
        elif status in ("running", "pending") and overall != "failed":
            overall = status
        items.append({
            "name": html.escape(s.get("name", "")),
            "status": status,
            "icon": STAGE_ICONS.get(s.get("type", ""), "⚙️"),
            "duration_s": dur,
            "logs_url": s.get("logs_url"),
        })
    return {"pipeline_id": pipeline_id, "stages": items, "overall": overall,
            "total_duration_s": total_duration, "stage_count": len(items),
            "timestamp": datetime.now(timezone.utc).isoformat()}
