"""App export data — app data export for migration/backup."""

import json
import html
from datetime import datetime, timezone


def build_export_manifest(*, app: dict, include: list[str] | None = None) -> dict:
    all_sections = ["settings", "webhooks", "api_keys", "analytics", "reviews", "changelog"]
    sections = include or all_sections
    items = []
    for s in sections:
        if s in all_sections:
            items.append({"section": s, "label": s.replace("_", " ").title(), "included": True,
                          "estimated_size_kb": {"settings": 5, "webhooks": 10, "api_keys": 2,
                                                 "analytics": 500, "reviews": 50, "changelog": 20}.get(s, 10)})
    total_kb = sum(i["estimated_size_kb"] for i in items)
    return {
        "app_name": html.escape(app.get("name", "")),
        "app_id": app.get("id", ""),
        "sections": items,
        "total_sections": len(items),
        "estimated_size_kb": total_kb,
        "estimated_size_display": f"{total_kb}KB" if total_kb < 1024 else f"{total_kb/1024:.1f}MB",
        "format": "json",
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
