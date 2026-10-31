"""Fleet DevContainer — track dev container environment health."""
from __future__ import annotations
def fleet_devcontainer_status(envs: list[dict]) -> dict:
    running = [e for e in envs if e.get("status") == "running"]
    failed = [e for e in envs if e.get("status") == "failed"]
    avg_startup = round(sum(e.get("startup_sec", 0) for e in running) / max(len(running), 1), 1)
    return {"total": len(envs), "running": len(running), "failed": len(failed),
            "avg_startup_sec": avg_startup, "fast": avg_startup < 60}
