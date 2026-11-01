"""Quick action — contextual actions for app management."""


ACTIONS = [
    {"id": "restart", "label": "Restart App", "icon": "🔄", "danger": False, "confirm": False},
    {"id": "deploy", "label": "Deploy Latest", "icon": "🚀", "danger": False, "confirm": False},
    {"id": "rollback", "label": "Rollback", "icon": "⏪", "danger": True, "confirm": True},
    {"id": "scale_up", "label": "Scale Up", "icon": "📈", "danger": False, "confirm": False},
    {"id": "scale_down", "label": "Scale Down", "icon": "📉", "danger": False, "confirm": True},
    {"id": "pause", "label": "Pause App", "icon": "⏸️", "danger": True, "confirm": True},
    {"id": "delete", "label": "Delete App", "icon": "🗑️", "danger": True, "confirm": True},
    {"id": "export", "label": "Export Config", "icon": "📦", "danger": False, "confirm": False},
]


def get_available_actions(*, app_status: str, user_role: str) -> dict:
    role_blocked = {"delete"} if user_role not in ("owner", "admin") else set()
    status_blocked = set()
    if app_status == "paused":
        status_blocked = {"pause", "scale_down"}
    elif app_status == "deleted":
        return {"actions": [], "total": 0}
    available = [a for a in ACTIONS if a["id"] not in role_blocked and a["id"] not in status_blocked]
    return {"actions": available, "total": len(available)}


def execute_action(*, action_id: str, confirmed: bool = False) -> dict:
    action = next((a for a in ACTIONS if a["id"] == action_id), None)
    if not action:
        return {"error": f"Unknown action: {action_id}"}
    if action["confirm"] and not confirmed:
        return {"error": "This action requires confirmation", "requires_confirm": True}
    return {"executed": True, "action": action_id, "label": action["label"]}
