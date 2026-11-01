"""Status dot — simple status indicator configurations."""


STATUS_MAP = {
    "online": {"color": "green", "label": "Online", "pulse": True},
    "offline": {"color": "gray", "label": "Offline", "pulse": False},
    "busy": {"color": "yellow", "label": "Busy", "pulse": True},
    "error": {"color": "red", "label": "Error", "pulse": True},
    "maintenance": {"color": "blue", "label": "Maintenance", "pulse": False},
}


def get_status_dot(*, status: str) -> dict:
    config = STATUS_MAP.get(status, STATUS_MAP["offline"])
    return {"status": status, **config}


def get_aggregate_status_dot(*, statuses: list[str]) -> dict:
    if not statuses:
        return get_status_dot(status="offline")
    if any(s == "error" for s in statuses):
        return get_status_dot(status="error")
    if any(s == "maintenance" for s in statuses):
        return get_status_dot(status="maintenance")
    if any(s == "busy" for s in statuses):
        return get_status_dot(status="busy")
    if all(s == "online" for s in statuses):
        return get_status_dot(status="online")
    return get_status_dot(status="offline")
