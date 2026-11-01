"""Cron history — scheduled job execution history."""

import html
from datetime import datetime, timezone


def build_cron_history(*, executions: list[dict]) -> dict:
    items = []
    success = failed = 0
    total_ms = 0
    for e in executions:
        status = e.get("status", "success")
        dur = e.get("duration_ms", 0)
        total_ms += dur
        if status == "success":
            success += 1
        else:
            failed += 1
        items.append({
            "job_name": html.escape(e.get("job_name", "")),
            "status": status,
            "duration_ms": dur,
            "started_at": e.get("started_at", ""),
            "output_lines": e.get("output_lines", 0),
        })
    items.sort(key=lambda x: x["started_at"], reverse=True)
    avg_ms = round(total_ms / max(len(items), 1))
    return {"executions": items[:20], "total": len(items),
            "success": success, "failed": failed,
            "avg_duration_ms": avg_ms,
            "success_rate": round(success / max(len(items), 1) * 100, 1)}
