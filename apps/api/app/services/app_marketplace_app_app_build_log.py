"""Build log — CI build log parser with step timing."""

import html
from datetime import datetime, timezone

STEP_ICONS = {"install": "📦", "build": "🔨", "test": "🧪", "lint": "🔍",
              "deploy": "🚀", "publish": "📤", "cleanup": "🧹"}


def parse_build_log(*, steps: list[dict]) -> dict:
    items = []
    total_ms = 0
    failed_step = None
    for s in steps:
        status = s.get("status", "success")
        duration_ms = s.get("duration_ms", 0)
        total_ms += duration_ms
        step = {
            "name": html.escape(s.get("name", "")),
            "status": status,
            "icon": STEP_ICONS.get(s.get("type", ""), "⚙️"),
            "duration_ms": duration_ms,
            "duration_display": f"{duration_ms}ms" if duration_ms < 1000 else f"{duration_ms/1000:.1f}s",
            "output_lines": s.get("output_lines", 0),
        }
        items.append(step)
        if status == "failed" and not failed_step:
            failed_step = step["name"]
    overall = "failed" if failed_step else "success"
    return {"steps": items, "total_steps": len(items), "overall": overall,
            "total_ms": total_ms, "failed_step": failed_step,
            "total_display": f"{total_ms/1000:.1f}s"}
