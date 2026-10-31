"""App Webhook Replay — replay failed webhook deliveries.

Manages webhook replay:
- Store failed deliveries for replay
- Replay individual or batch
- Track replay attempts and outcomes
- Per-installation scoped replays
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class FailedDelivery:
    """A failed webhook delivery eligible for replay."""

    delivery_id: str
    destination: str
    event_type: str
    payload: str
    original_status: int
    failed_at: float = field(default_factory=time.time)
    replay_count: int = 0
    last_replay_status: int | None = None
    resolved: bool = False


class AppWebhookReplay:
    """Replay failed webhook deliveries."""

    def __init__(self, max_replays: int = 3) -> None:
        self._max_replays = max_replays
        self._deliveries: dict[tuple[str, str], FailedDelivery] = {}

    def record_failure(
        self, installation_id: str, delivery_id: str, destination: str,
        event_type: str, payload: str, status_code: int,
    ) -> FailedDelivery:
        if not installation_id:
            raise ValueError("installation_id is required")

        fd = FailedDelivery(
            delivery_id=delivery_id, destination=destination,
            event_type=event_type, payload=payload,
            original_status=status_code,
        )
        self._deliveries[(installation_id, delivery_id)] = fd
        return fd

    def replay(self, installation_id: str, delivery_id: str, result_status: int) -> FailedDelivery:
        fd = self._get(installation_id, delivery_id)
        if fd.resolved:
            raise ValueError("Already resolved")
        if fd.replay_count >= self._max_replays:
            raise ValueError("Max replay attempts reached")

        fd.replay_count += 1
        fd.last_replay_status = result_status
        if 200 <= result_status < 300:
            fd.resolved = True
        return fd

    def pending(self, installation_id: str) -> list[FailedDelivery]:
        return [
            fd for (inst, _), fd in self._deliveries.items()
            if inst == installation_id and not fd.resolved and fd.replay_count < self._max_replays
        ]

    def resolved_count(self, installation_id: str) -> int:
        return sum(
            1 for (inst, _), fd in self._deliveries.items()
            if inst == installation_id and fd.resolved
        )

    def list_all(self, installation_id: str) -> list[FailedDelivery]:
        return [fd for (inst, _), fd in self._deliveries.items() if inst == installation_id]

    def _get(self, installation_id: str, delivery_id: str) -> FailedDelivery:
        key = (installation_id, delivery_id)
        fd = self._deliveries.get(key)
        if fd is None:
            raise KeyError(f"Delivery {delivery_id} not found")
        return fd
