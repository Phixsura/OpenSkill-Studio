"""App Webhook Replay — replay failed webhook deliveries.

Manages webhook replay for installed apps:
- Queue failed deliveries for replay
- Track replay status
- Configurable delay between replays
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum

import structlog

log = structlog.get_logger()


class ReplayStatus(str, Enum):
    QUEUED = "queued"
    REPLAYING = "replaying"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


@dataclass
class ReplayRequest:
    """A webhook replay request."""

    replay_id: str
    installation_id: str
    original_event_id: str
    webhook_url: str
    payload: str
    status: ReplayStatus = ReplayStatus.QUEUED
    attempt: int = 0
    max_attempts: int = 3
    created_at: float = field(default_factory=time.time)
    completed_at: float | None = None
    error: str = ""


class AppWebhookReplay:
    """Replay failed webhook deliveries."""

    def __init__(self) -> None:
        self._replays: dict[tuple[str, str], ReplayRequest] = {}

    def queue_replay(
        self,
        installation_id: str,
        replay_id: str,
        original_event_id: str,
        webhook_url: str,
        payload: str,
        max_attempts: int = 3,
        now: float | None = None,
    ) -> ReplayRequest:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not replay_id:
            raise ValueError("replay_id is required")
        if not webhook_url:
            raise ValueError("webhook_url is required")

        key = (installation_id, replay_id)
        if key in self._replays:
            raise ValueError(f"Replay {replay_id} already exists")

        req = ReplayRequest(
            replay_id=replay_id, installation_id=installation_id,
            original_event_id=original_event_id, webhook_url=webhook_url,
            payload=payload, max_attempts=max(1, max_attempts),
            created_at=now or time.time(),
        )
        self._replays[key] = req
        return req

    def start_replay(self, installation_id: str, replay_id: str) -> ReplayRequest:
        req = self._get(installation_id, replay_id)
        if req.status not in (ReplayStatus.QUEUED, ReplayStatus.FAILED):
            raise ValueError(f"Cannot replay in {req.status} state")
        req.status = ReplayStatus.REPLAYING
        req.attempt += 1
        return req

    def succeed_replay(self, installation_id: str, replay_id: str) -> ReplayRequest:
        req = self._get(installation_id, replay_id)
        if req.status != ReplayStatus.REPLAYING:
            raise ValueError("Not currently replaying")
        req.status = ReplayStatus.SUCCEEDED
        req.completed_at = time.time()
        return req

    def fail_replay(self, installation_id: str, replay_id: str, error: str = "") -> ReplayRequest:
        req = self._get(installation_id, replay_id)
        if req.status != ReplayStatus.REPLAYING:
            raise ValueError("Not currently replaying")
        req.error = error
        if req.attempt >= req.max_attempts:
            req.status = ReplayStatus.FAILED
            req.completed_at = time.time()
        else:
            req.status = ReplayStatus.QUEUED  # re-queue for retry
        return req

    def list_replays(self, installation_id: str, status: ReplayStatus | None = None) -> list[ReplayRequest]:
        replays = [r for (inst, _), r in self._replays.items() if inst == installation_id]
        if status:
            replays = [r for r in replays if r.status == status]
        return replays

    def _get(self, installation_id: str, replay_id: str) -> ReplayRequest:
        key = (installation_id, replay_id)
        req = self._replays.get(key)
        if req is None:
            raise KeyError(f"Replay {replay_id} not found")
        return req
