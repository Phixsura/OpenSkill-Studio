"""System notification — platform-wide announcements and alerts."""

import secrets
from datetime import datetime, timedelta


SEVERITY_LEVELS = {"info": 0, "warning": 1, "critical": 2, "maintenance": 1}


def create_system_notification(*, title: str, message: str, severity: str = "info",
                                  expires_hours: int = 24, dismissible: bool = True) -> dict:
    if severity not in SEVERITY_LEVELS:
        return {"error": f"Invalid severity. Valid: {', '.join(sorted(SEVERITY_LEVELS))}"}
    now = datetime.utcnow()
    return {
        "notification_id": f"sys_{secrets.token_urlsafe(8)}",
        "title": title,
        "message": message,
        "severity": severity,
        "dismissible": dismissible,
        "created_at": now.isoformat(),
        "expires_at": (now + timedelta(hours=expires_hours)).isoformat(),
        "active": True,
    }


def get_active_notifications(*, notifications: list[dict]) -> dict:
    now = datetime.utcnow().isoformat()
    active = [n for n in notifications if n.get("active") and n.get("expires_at", "") > now]
    active.sort(key=lambda n: SEVERITY_LEVELS.get(n.get("severity", "info"), 0), reverse=True)
    return {"notifications": active, "count": len(active),
            "has_critical": any(n.get("severity") == "critical" for n in active)}
