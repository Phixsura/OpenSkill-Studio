"""Fleet Fine-tuning — track model fine-tuning jobs."""
from __future__ import annotations
def fleet_finetune_status(jobs: list[dict]) -> dict:
    running = [j for j in jobs if j.get("status") == "running"]
    completed = [j for j in jobs if j.get("status") == "completed"]
    failed = [j for j in jobs if j.get("status") == "failed"]
    total_epochs = sum(j.get("epochs", 0) for j in completed)
    return {"total": len(jobs), "running": len(running), "completed": len(completed),
            "failed": len(failed), "total_epochs": total_epochs}
