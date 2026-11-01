"""Data retention — retention policy management and cleanup scheduling."""

import html
from datetime import datetime, timezone, timedelta

PRESETS = {
    "30d": {"days": 30, "label": "30 days"},
    "90d": {"days": 90, "label": "90 days"},
    "1y": {"days": 365, "label": "1 year"},
    "3y": {"days": 1095, "label": "3 years"},
    "forever": {"days": None, "label": "Forever"},
}


def build_retention_policy(*, data_types: list[dict]) -> dict:
    items = []
    for dt in data_types:
        preset = PRESETS.get(dt.get("retention", "90d"), PRESETS["90d"])
        days = preset["days"]
        items.append({
            "type": html.escape(dt.get("type", "")),
            "description": html.escape(dt.get("description", "")),
            "retention": preset["label"],
            "retention_days": days,
            "auto_delete": days is not None,
        })
    auto_delete_count = sum(1 for i in items if i["auto_delete"])
    return {"policies": items, "total": len(items), "auto_delete_count": auto_delete_count}


def estimate_cleanup(*, record_count: int, retention_days: int, daily_growth: int = 100) -> dict:
    eligible = max(0, record_count - (retention_days * daily_growth))
    return {"eligible_for_deletion": eligible, "retention_days": retention_days,
            "estimated_storage_saved_mb": round(eligible * 0.002, 1)}
