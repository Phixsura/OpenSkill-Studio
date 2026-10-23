"""Deployment log viewer — structured deploy logs with step tracking."""
from __future__ import annotations
import html


def build_deploy_log(steps: list[dict]) -> dict:
    log_lines = []
    total_duration = 0
    for s in steps:
        duration = s.get("duration_ms", 0)
        total_duration += duration
        status = s.get("status", "pending")
        icon = {"success": "✅", "failed": "❌", "running": "🔄", "pending": "⬜"}.get(status, "⬜")
        log_lines.append({
            "step": html.escape(s.get("name", "")), "status": status, "icon": icon,
            "duration_ms": duration, "output": s.get("output", ""),
        })
    failed = sum(1 for l in log_lines if l["status"] == "failed")
    return {
        "lines": log_lines, "total_steps": len(log_lines),
        "completed": sum(1 for l in log_lines if l["status"] == "success"),
        "failed": failed, "total_duration_ms": total_duration,
        "duration_display": f"{total_duration / 1000:.1f}s",
        "overall": "failed" if failed else "success" if all(l["status"] == "success" for l in log_lines) else "in_progress",
    }
