"""Cron job monitor — track cron job executions and failures."""
from __future__ import annotations


class CronMonitor:
    def __init__(self):
        self._jobs: dict[str, dict] = {}

    def register(self, name: str, schedule: str) -> dict:
        self._jobs[name] = {"name": name, "schedule": schedule,
                             "runs": 0, "failures": 0, "last_status": "pending"}
        return self._jobs[name]

    def record_run(self, name: str, success: bool, duration_ms: float) -> dict:
        job = self._jobs[name]
        job["runs"] += 1
        if not success:
            job["failures"] += 1
        job["last_status"] = "success" if success else "failed"
        job["last_duration_ms"] = duration_ms
        return {"name": name, "status": job["last_status"], "run": job["runs"]}

    def failing_jobs(self) -> list[dict]:
        return [j for j in self._jobs.values() if j["last_status"] == "failed"]

    def stats(self) -> dict:
        total_runs = sum(j["runs"] for j in self._jobs.values())
        total_failures = sum(j["failures"] for j in self._jobs.values())
        return {"total_jobs": len(self._jobs), "total_runs": total_runs,
                "total_failures": total_failures,
                "success_rate": round((total_runs - total_failures) / max(total_runs, 1) * 100, 1)}
