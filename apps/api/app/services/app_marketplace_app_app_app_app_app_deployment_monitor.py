"""Deployment monitor — real-time deployment progress tracker."""

import html
from datetime import datetime, timezone

DEPLOY_PHASES = [
    {"id": "build", "label": "Build", "icon": "🔨"},
    {"id": "test", "label": "Test", "icon": "🧪"},
    {"id": "deploy", "label": "Deploy", "icon": "🚀"},
    {"id": "verify", "label": "Verify", "icon": "✅"},
]


def build_deployment_monitor(*, deploy_id: str, app_name: str, version: str,
                                environment: str, phase_statuses: dict[str, str]) -> dict:
    phases = []
    current_phase = None
    for p in DEPLOY_PHASES:
        status = phase_statuses.get(p["id"], "pending")
        phases.append({**p, "status": status,
                        "status_icon": {"completed": "✅", "running": "⏳", "failed": "❌", "pending": "⬜"}.get(status, "⬜")})
        if status == "running":
            current_phase = p["id"]
    completed = sum(1 for p in phases if p["status"] == "completed")
    failed = any(p["status"] == "failed" for p in phases)
    progress = round(completed / len(phases) * 100)
    overall = "failed" if failed else "success" if completed == len(phases) else "in_progress"
    return {
        "deploy_id": deploy_id, "app_name": html.escape(app_name),
        "version": version, "environment": environment,
        "phases": phases, "current_phase": current_phase,
        "progress": progress, "overall": overall,
        "started_at": datetime.now(timezone.utc).isoformat(),
    }
