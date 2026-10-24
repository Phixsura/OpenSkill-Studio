"""Fleet AI Fine-Tuning — track model fine-tuning jobs."""
from __future__ import annotations
def fleet_ai_finetune(jobs: list[dict]) -> dict:
    running = [j for j in jobs if j.get("status") == "running"]
    completed = [j for j in jobs if j.get("status") == "completed"]
    failed = [j for j in jobs if j.get("status") == "failed"]
    total_epochs = sum(j.get("epochs", 0) for j in jobs)
    return {"jobs": len(jobs), "running": len(running), "completed": len(completed),
            "failed": len(failed), "total_epochs": total_epochs, "success_rate": round(len(completed) / max(len(jobs), 1) * 100, 1)}
