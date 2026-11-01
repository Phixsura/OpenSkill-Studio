"""API Consumer Webhook Replay — replay failed webhook deliveries."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
import time
import structlog

log = structlog.get_logger()

class ReplayStatus(str, Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"

@dataclass
class ReplayRequest:
    replay_id: str
    original_event_id: str
    consumer_id: str
    endpoint: str
    status: ReplayStatus = ReplayStatus.PENDING
    original_failure_reason: str = ""
    replayed_at: float = 0.0
    response_status: int = 0

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiWebhookReplay:
    def __init__(self, max_replays_per_event: int = 3) -> None:
        self._replays: dict[str, list[ReplayRequest]] = {}
        self._max_per_event = max(1, max_replays_per_event)

    def request_replay(self, installation_id: str, replay: ReplayRequest) -> ReplayRequest:
        if not installation_id: raise ValueError("installation_id is required")
        existing = [r for r in self._replays.get(installation_id, []) if r.original_event_id == replay.original_event_id]
        if len(existing) >= self._max_per_event:
            raise ValueError(f"Max {self._max_per_event} replays per event reached")
        self._replays.setdefault(installation_id, []).append(replay)
        return replay

    def complete_replay(self, installation_id: str, replay_id: str, response_status: int) -> ReplayRequest:
        for r in self._replays.get(installation_id, []):
            if r.replay_id == replay_id:
                r.status = ReplayStatus.SUCCESS if 200 <= response_status < 300 else ReplayStatus.FAILED
                r.response_status = response_status
                r.replayed_at = time.time()
                return r
        raise KeyError(f"Replay {replay_id} not found")

    def pending_replays(self, installation_id: str) -> list[ReplayRequest]:
        return [r for r in self._replays.get(installation_id, []) if r.status == ReplayStatus.PENDING]

    def replay_stats(self, installation_id: str) -> dict[str, int]:
        replays = self._replays.get(installation_id, [])
        return {"total": len(replays), "pending": sum(1 for r in replays if r.status == ReplayStatus.PENDING), "success": sum(1 for r in replays if r.status == ReplayStatus.SUCCESS), "failed": sum(1 for r in replays if r.status == ReplayStatus.FAILED)}

    def replay_count(self, installation_id: str) -> int:
        return len(self._replays.get(installation_id, []))
