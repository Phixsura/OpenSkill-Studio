"""Sandbox Cron — cron job management for extension sandboxes.

Registers cron-like schedules with expression parsing, next-run
calculation, execution tracking, and missed-run detection.
"""
from __future__ import annotations
import secrets
import time
from dataclasses import dataclass, field
from enum import Enum


class CronStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    DISABLED = "disabled"


@dataclass
class CronJob:
    job_id: str
    sandbox_id: str
    name: str
    expression: str  # simplified: "every Xm" or "every Xh" or "daily HH:MM"
    command: str
    status: CronStatus = CronStatus.ACTIVE
    interval_seconds: int = 0
    last_run_at: float = 0.0
    next_run_at: float = 0.0
    run_count: int = 0
    failure_count: int = 0
    max_failures: int = 5


def parse_expression(expr: str) -> int:
    """Parse simplified cron expression to interval in seconds."""
    expr = expr.strip().lower()
    if expr.startswith("every "):
        part = expr[6:].strip()
        if part.endswith("m"):
            return int(part[:-1]) * 60
        if part.endswith("h"):
            return int(part[:-1]) * 3600
        if part.endswith("s"):
            return int(part[:-1])
    if expr.startswith("daily"):
        return 86400
    raise ValueError(f"Invalid cron expression: {expr}")


class SandboxCronService:
    """Manages cron jobs for extension sandboxes."""

    def __init__(self):
        self._jobs: dict[str, CronJob] = {}

    def register(self, sandbox_id: str, name: str, expression: str,
                 command: str) -> CronJob:
        interval = parse_expression(expression)
        if interval < 60:
            raise ValueError("Minimum interval is 60 seconds")

        job_id = f"cron_{secrets.token_urlsafe(8)}"
        job = CronJob(
            job_id=job_id, sandbox_id=sandbox_id, name=name,
            expression=expression, command=command,
            interval_seconds=interval,
            next_run_at=time.time() + interval,
        )
        self._jobs[job_id] = job
        return job

    def tick(self, now: float | None = None) -> list[CronJob]:
        """Find all jobs due for execution."""
        current = now or time.time()
        due = []
        for job in self._jobs.values():
            if job.status != CronStatus.ACTIVE:
                continue
            if current >= job.next_run_at:
                due.append(job)
        return due

    def record_run(self, job_id: str, success: bool = True) -> bool:
        job = self._jobs.get(job_id)
        if not job:
            return False
        job.run_count += 1
        job.last_run_at = time.time()
        job.next_run_at = time.time() + job.interval_seconds
        if not success:
            job.failure_count += 1
            if job.failure_count >= job.max_failures:
                job.status = CronStatus.DISABLED
        return True

    def pause(self, job_id: str) -> bool:
        job = self._jobs.get(job_id)
        if job and job.status == CronStatus.ACTIVE:
            job.status = CronStatus.PAUSED
            return True
        return False

    def resume(self, job_id: str) -> bool:
        job = self._jobs.get(job_id)
        if job and job.status == CronStatus.PAUSED:
            job.status = CronStatus.ACTIVE
            job.next_run_at = time.time() + job.interval_seconds
            return True
        return False

    def delete(self, job_id: str) -> bool:
        return self._jobs.pop(job_id, None) is not None

    def list_jobs(self, sandbox_id: str) -> list[CronJob]:
        return [j for j in self._jobs.values() if j.sandbox_id == sandbox_id]

    def get_stats(self, sandbox_id: str) -> dict:
        jobs = self.list_jobs(sandbox_id)
        return {
            "total": len(jobs),
            "active": sum(1 for j in jobs if j.status == CronStatus.ACTIVE),
            "paused": sum(1 for j in jobs if j.status == CronStatus.PAUSED),
            "disabled": sum(1 for j in jobs if j.status == CronStatus.DISABLED),
            "total_runs": sum(j.run_count for j in jobs),
        }
