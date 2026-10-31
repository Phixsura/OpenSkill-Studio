"""App API Developer Webhook Replay Manager — replay failed webhook deliveries."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class ReplayRequest:
    replay_id: str
    original_delivery_id: str
    destination: str
    event_type: str
    status: str = "pending"  # "pending", "replaying", "success", "failure"
    created_at: float = field(default_factory=time.time)
    replayed_at: float | None = None

class AppAPIDeveloperAPIApiWebhookReplayManager:
    def __init__(self) -> None:
        self._replays: dict[tuple[str, str], ReplayRequest] = {}

    def request_replay(self, installation_id: str, replay_id: str, original_delivery_id: str, destination: str, event_type: str) -> ReplayRequest:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, replay_id)
        if key in self._replays: raise ValueError(f"Replay {replay_id} exists")
        r = ReplayRequest(replay_id=replay_id, original_delivery_id=original_delivery_id, destination=destination, event_type=event_type)
        self._replays[key] = r
        return r

    def start_replay(self, installation_id: str, replay_id: str) -> ReplayRequest:
        r = self._get(installation_id, replay_id)
        r.status = "replaying"
        return r

    def complete_replay(self, installation_id: str, replay_id: str, success: bool) -> ReplayRequest:
        r = self._get(installation_id, replay_id)
        r.status = "success" if success else "failure"
        r.replayed_at = time.time()
        return r

    def pending_replays(self, installation_id: str) -> list[ReplayRequest]:
        return [r for (inst, _), r in self._replays.items() if inst == installation_id and r.status in ("pending", "replaying")]

    def replay_stats(self, installation_id: str) -> dict[str, int]:
        replays = [r for (inst, _), r in self._replays.items() if inst == installation_id]
        return {s: sum(1 for r in replays if r.status == s) for s in ("pending", "replaying", "success", "failure")}

    def _get(self, installation_id: str, replay_id: str) -> ReplayRequest:
        key = (installation_id, replay_id)
        r = self._replays.get(key)
        if r is None: raise KeyError(f"Replay {replay_id} not found")
        return r
