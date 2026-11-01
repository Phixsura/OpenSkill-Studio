"""Activity indicator — show active/idle/away user status."""


STATUS_CONFIGS = {
    "active": {"label": "Active now", "color": "green", "dot": "🟢", "timeout_min": 5},
    "idle": {"label": "Idle", "color": "yellow", "dot": "🟡", "timeout_min": 30},
    "away": {"label": "Away", "color": "gray", "dot": "⚪", "timeout_min": 60},
    "offline": {"label": "Offline", "color": "gray", "dot": "⚫", "timeout_min": None},
    "dnd": {"label": "Do Not Disturb", "color": "red", "dot": "🔴", "timeout_min": None},
}


def get_user_status(*, last_active_min_ago: int, manual_status: str | None = None) -> dict:
    if manual_status and manual_status in STATUS_CONFIGS:
        return {"status": manual_status, **STATUS_CONFIGS[manual_status]}
    if last_active_min_ago <= 5:
        status = "active"
    elif last_active_min_ago <= 30:
        status = "idle"
    elif last_active_min_ago <= 60:
        status = "away"
    else:
        status = "offline"
    return {"status": status, **STATUS_CONFIGS[status], "last_active_min_ago": last_active_min_ago}
