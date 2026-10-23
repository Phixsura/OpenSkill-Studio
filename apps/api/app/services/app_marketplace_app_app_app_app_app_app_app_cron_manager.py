"""Cron job manager — schedule, track, and monitor recurring jobs."""
from __future__ import annotations
import time


class CronJobManager:
    def __init__(self):
        self._jobs: dict[str, dict] = {}

    def schedule(self, *, job_id: str, name: str, schedule: str,
                  command: str, enabled: bool = True) -> dict:
        self._jobs[job_id] = {
            "id": job_id, "name": name, "schedule": schedule,
            "command": command, "enabled": enabled,
            "last_run": None, "last_status": None,
            "run_count": 0, "fail_count": 0,
        }
        return {"job_id": job_id, "name": name, "schedule": schedule, "status": "scheduled"}

    def record_run(self, job_id: str, *, success: bool, duration_ms: int = 0) -> dict:
        job = self._jobs.get(job_id)
        if not job:
            return {"error": "Job not found"}
        job["run_count"] += 1
        job["last_run"] = time.time()
        job["last_status"] = "success" if success else "failed"
        if not success:
            job["fail_count"] += 1
        return {"job_id": job_id, "run_count": job["run_count"],
                "last_status": job["last_status"], "duration_ms": duration_ms}

    def list_jobs(self) -> list[dict]:
        return [{"id": j["id"], "name": j["name"], "schedule": j["schedule"],
                 "enabled": j["enabled"], "last_status": j["last_status"],
                 "run_count": j["run_count"], "fail_count": j["fail_count"],
                 "success_rate": round((j["run_count"] - j["fail_count"]) / max(j["run_count"], 1) * 100)}
                for j in self._jobs.values()]

    def toggle(self, job_id: str) -> dict:
        job = self._jobs.get(job_id)
        if not job:
            return {"error": "Job not found"}
        job["enabled"] = not job["enabled"]
        return {"job_id": job_id, "enabled": job["enabled"]}
