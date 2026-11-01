"""Extension Cron Scheduler — scheduled tasks for extensions."""
from __future__ import annotations
from dataclasses import dataclass
import re
import time

CRON_RE = re.compile(r'^(\*|[0-9,/*-]+)\s+(\*|[0-9,/*-]+)\s+(\*|[0-9,/*-]+)\s+(\*|[0-9,/*-]+)\s+(\*|[0-9,/*-]+)$')


@dataclass
class CronJob:
    job_id: str
    extension_id: str
    name: str
    schedule: str  # cron expression
    handler: str  # function/endpoint to call
    enabled: bool = True
    last_run: float = 0.0
    run_count: int = 0
    max_retries: int = 3
    created_at: float = 0.0
    def __post_init__(self):
        if not self.created_at: self.created_at = time.time()


class ExtCronSchedulerService:
    def __init__(self):
        self._jobs: dict[str, CronJob] = {}
        self._counter = 0

    def create(self, extension_id: str, name: str, schedule: str,
               handler: str, max_retries: int = 3) -> CronJob:
        if not CRON_RE.match(schedule):
            raise ValueError(f"Invalid cron expression: {schedule}")
        self._counter += 1
        job = CronJob(job_id=f"cron-{self._counter}", extension_id=extension_id,
                      name=name, schedule=schedule, handler=handler,
                      max_retries=max_retries)
        self._jobs[job.job_id] = job
        return job

    def trigger(self, job_id: str) -> bool:
        job = self._jobs.get(job_id)
        if not job or not job.enabled:
            return False
        job.last_run = time.time()
        job.run_count += 1
        return True

    def toggle(self, job_id: str, enabled: bool) -> bool:
        job = self._jobs.get(job_id)
        if not job: return False
        job.enabled = enabled
        return True

    def get_by_extension(self, extension_id: str) -> list[CronJob]:
        return [j for j in self._jobs.values() if j.extension_id == extension_id]

    def delete(self, job_id: str) -> bool:
        return self._jobs.pop(job_id, None) is not None
