"""App install flow — multi-step installation wizard with permission grants."""
from __future__ import annotations
import html


def build_install_flow(app: dict) -> dict:
    permissions = app.get("permissions", [])
    has_dangerous = any(p.get("risk") == "high" for p in permissions)
    steps = [
        {"id": "review", "title": "Review Permissions", "status": "current"},
        {"id": "configure", "title": "Configure Settings", "status": "pending"},
        {"id": "connect", "title": "Connect Account", "status": "pending"},
        {"id": "activate", "title": "Activate", "status": "pending"},
    ]
    return {
        "app_name": html.escape(app.get("name", "")),
        "app_icon": app.get("icon", "📱"),
        "developer": html.escape(app.get("developer", "")),
        "version": app.get("version", ""),
        "permissions": [{"name": p.get("name", ""), "description": html.escape(p.get("description", "")),
                           "risk": p.get("risk", "low")} for p in permissions],
        "has_dangerous_permissions": has_dangerous,
        "steps": steps, "total_steps": len(steps), "current_step": 0,
    }


def advance_step(flow: dict, step_index: int) -> dict:
    if step_index >= len(flow["steps"]):
        return {"error": "Invalid step"}
    flow["steps"][step_index]["status"] = "completed"
    if step_index + 1 < len(flow["steps"]):
        flow["steps"][step_index + 1]["status"] = "current"
    flow["current_step"] = step_index + 1
    done = all(s["status"] == "completed" for s in flow["steps"])
    return {"step_completed": step_index, "done": done,
            "progress": f"{step_index + 1}/{flow['total_steps']}"}
