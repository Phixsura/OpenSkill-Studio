"""API Consumer Webhook Event Replay Policy — define policies for event replay."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class ReplayPolicy:
    consumer_id: str
    max_replays_per_event: int = 3
    replay_window_hours: int = 24
    auto_replay_on_failure: bool = False
    replay_delay_s: int = 60

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookEventReplayPolicy:
    def __init__(self) -> None:
        self._policies: dict[tuple[str, str], ReplayPolicy] = {}
        self._replay_counts: dict[tuple[str, str, str], int] = {}

    def set_policy(self, installation_id: str, policy: ReplayPolicy) -> ReplayPolicy:
        if not installation_id: raise ValueError("installation_id is required")
        if policy.max_replays_per_event < 1: raise ValueError("max_replays must be >= 1")
        if policy.replay_delay_s < 0: raise ValueError("delay must be non-negative")
        self._policies[(installation_id, policy.consumer_id)] = policy
        return policy

    def can_replay(self, installation_id: str, consumer_id: str, event_id: str) -> bool:
        policy = self._policies.get((installation_id, consumer_id))
        if policy is None: return False
        count = self._replay_counts.get((installation_id, consumer_id, event_id), 0)
        return count < policy.max_replays_per_event

    def record_replay(self, installation_id: str, consumer_id: str, event_id: str) -> int:
        if not self.can_replay(installation_id, consumer_id, event_id):
            raise ValueError("Max replays reached for this event")
        key = (installation_id, consumer_id, event_id)
        self._replay_counts[key] = self._replay_counts.get(key, 0) + 1
        return self._replay_counts[key]

    def get_policy(self, installation_id: str, consumer_id: str) -> ReplayPolicy | None:
        return self._policies.get((installation_id, consumer_id))

    def list_policies(self, installation_id: str) -> list[ReplayPolicy]:
        return [p for (inst, _), p in self._policies.items() if inst == installation_id]
