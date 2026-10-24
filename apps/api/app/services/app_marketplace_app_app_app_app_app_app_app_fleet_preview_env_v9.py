"""Fleet Preview Env v9 — track ephemeral preview environment lifecycle."""
from __future__ import annotations
def fleet_preview_env_v9(envs: list[dict]) -> dict:
    running = [e for e in envs if e.get("status") == "running"]
    expired = [e for e in envs if e.get("status") == "expired"]
    avg_age = sum(e.get("age_hours", 0) for e in envs) / len(envs) if envs else 0
    return {"total": len(envs), "running": len(running), "expired": len(expired),
            "avg_age_hours": round(avg_age, 1), "healthy": len(expired) < len(envs) * 0.2}
