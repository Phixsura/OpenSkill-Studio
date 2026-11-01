"""App API Developer Webhook Event Replay Scheduler — schedule and manage event replays."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class ReplayJob:
    job_id: str
    destination: str
    event_ids: list[str] = field(default_factory=list)
    status: str = "pending"  # "pending", "running", "completed", "failed"
    replayed: int = 0
    failed_count: int = 0
    created_at: float = field(default_factory=time.time)

    @property
    def total(self) -> int:
        return len(self.event_ids)

    @property
    def progress_pct(self) -> float:
        return round((self.replayed + self.failed_count) / self.total * 100, 1) if self.total > 0 else 0.0

class AppAPIDeveloperPlatformSDKApiPlatformApiWebhookEventReplayScheduler:
    def __init__(self) -> None:
        self._jobs: dict[tuple[str, str], ReplayJob] = {}

    def schedule(self, installation_id: str, job_id: str, destination: str, event_ids: list[str]) -> ReplayJob:
        if not installation_id: raise ValueError("installation_id is required")
        if not event_ids: raise ValueError("event_ids must not be empty")
        key = (installation_id, job_id)
        j = ReplayJob(job_id=job_id, destination=destination, event_ids=event_ids)
        self._jobs[key] = j
        return j

    def process(self, installation_id: str, job_id: str, success: bool) -> ReplayJob:
        key = (installation_id, job_id)
        j = self._jobs.get(key)
        if j is None: raise KeyError(f"Job {job_id} not found")
        if j.status == "pending": j.status = "running"
        if success: j.replayed += 1
        else: j.failed_count += 1
        if j.replayed + j.failed_count >= j.total:
            j.status = "completed" if j.failed_count == 0 else "failed"
        return j

    def active_jobs(self, installation_id: str) -> list[ReplayJob]:
        return [j for (inst, _), j in self._jobs.items() if inst == installation_id and j.status in ("pending", "running")]

    def all_jobs(self, installation_id: str) -> list[ReplayJob]:
        return [j for (inst, _), j in self._jobs.items() if inst == installation_id]
