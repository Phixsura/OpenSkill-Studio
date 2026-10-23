"""Data pipeline orchestrator — define, run, and monitor ETL pipelines."""
from __future__ import annotations
import time


class DataPipeline:
    def __init__(self, name: str, steps: list[dict]):
        self.name = name
        self.steps = [{"name": s["name"], "type": s.get("type", "transform"),
                        "status": "pending", "duration_ms": 0, "records": 0,
                        "error": None} for s in steps]
        self.status = "idle"
        self.started: float = 0

    def start(self) -> dict:
        self.status = "running"
        self.started = time.time()
        return {"pipeline": self.name, "status": "running", "steps": len(self.steps)}

    def complete_step(self, index: int, *, records: int = 0, duration_ms: int = 0,
                       error: str | None = None) -> dict:
        if index >= len(self.steps):
            return {"error": "Step index out of range"}
        step = self.steps[index]
        step["status"] = "failed" if error else "completed"
        step["records"] = records
        step["duration_ms"] = duration_ms
        step["error"] = error
        if error:
            self.status = "failed"
        elif all(s["status"] == "completed" for s in self.steps):
            self.status = "completed"
        return {"step": step["name"], "status": step["status"], "records": records}

    def summary(self) -> dict:
        total_records = sum(s["records"] for s in self.steps)
        total_duration = sum(s["duration_ms"] for s in self.steps)
        completed = sum(1 for s in self.steps if s["status"] == "completed")
        failed = sum(1 for s in self.steps if s["status"] == "failed")
        return {"pipeline": self.name, "status": self.status,
                "steps_total": len(self.steps), "steps_completed": completed,
                "steps_failed": failed, "total_records": total_records,
                "total_duration_ms": total_duration,
                "duration_display": f"{total_duration / 1000:.1f}s"}
