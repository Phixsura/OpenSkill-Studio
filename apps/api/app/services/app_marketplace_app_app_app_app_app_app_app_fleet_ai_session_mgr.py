"""Fleet AI Session Manager — track user session and context persistence."""
from __future__ import annotations
def fleet_ai_session_manager(managers: list[dict]) -> dict:
    active = [m for m in managers if m.get("active", True)]
    sessions_active = sum(m.get("sessions", 0) for m in managers)
    avg_duration_min = round(sum(m.get("avg_duration_min", 0) for m in managers) / max(len(managers), 1), 1)
    persistence_rate = round(sum(m.get("persistence_pct", 0) for m in managers) / max(len(managers), 1), 1)
    return {"managers": len(managers), "active": len(active), "sessions": sessions_active,
            "avg_duration_min": avg_duration_min, "persistence_rate": persistence_rate, "persistent": persistence_rate > 95}
