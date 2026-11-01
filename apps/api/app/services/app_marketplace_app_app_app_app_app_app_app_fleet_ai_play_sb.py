"""Fleet AI Playground Sandbox — track isolated AI experimentation envs."""
from __future__ import annotations
def fleet_ai_playground_sandbox(sandboxes: list[dict]) -> dict:
    active = [s for s in sandboxes if s.get("active", True)]
    sessions_24h = sum(s.get("sessions_24h", 0) for s in sandboxes)
    avg_duration_min = round(sum(s.get("duration_min", 0) for s in sandboxes) / max(len(sandboxes), 1), 1)
    models_available = sum(s.get("models", 0) for s in sandboxes)
    return {"sandboxes": len(sandboxes), "active": len(active), "sessions_24h": sessions_24h,
            "avg_duration_min": avg_duration_min, "models": models_available, "engaging": sessions_24h > 100}
