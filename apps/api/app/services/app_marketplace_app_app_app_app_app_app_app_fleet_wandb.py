"""Fleet W&B — track ML experiment tracking."""
from __future__ import annotations
def fleet_wandb_status(projects: list[dict]) -> dict:
    active = [p for p in projects if p.get("active", True)]
    runs_24h = sum(p.get("runs_24h", 0) for p in projects)
    artifacts = sum(p.get("artifacts", 0) for p in projects)
    return {"projects": len(projects), "active": len(active), "runs_24h": runs_24h,
            "artifacts": artifacts, "all_active": len(active) == len(projects)}
