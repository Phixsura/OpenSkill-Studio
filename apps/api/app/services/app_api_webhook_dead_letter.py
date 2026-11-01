"""App API Webhook Dead Letter — manage permanently failed webhook deliveries.

Manages dead letter storage:
- Store failed deliveries after max retries
- Inspect and retry dead letters
- Purge old entries
- Per-installation scoped dead letters
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class DeadLetter:
    """A permanently failed webhook delivery."""

    letter_id: str
    destination: str
    event_type: str
    payload: str
    last_error: str
    attempts: int
    failed_at: float = field(default_factory=time.time)
    retried: bool = False


class AppAPIWebhookDeadLetter:
    """Manage permanently failed webhook deliveries."""

    def __init__(self) -> None:
        self._letters: dict[tuple[str, str], DeadLetter] = {}

    def store(
        self, installation_id: str, letter_id: str, destination: str,
        event_type: str, payload: str, last_error: str, attempts: int,
    ) -> DeadLetter:
        if not installation_id:
            raise ValueError("installation_id is required")
        dl = DeadLetter(
            letter_id=letter_id, destination=destination,
            event_type=event_type, payload=payload,
            last_error=last_error, attempts=attempts,
        )
        self._letters[(installation_id, letter_id)] = dl
        return dl

    def mark_retried(self, installation_id: str, letter_id: str) -> DeadLetter:
        dl = self._get(installation_id, letter_id)
        dl.retried = True
        return dl

    def pending(self, installation_id: str) -> list[DeadLetter]:
        return [dl for (inst, _), dl in self._letters.items() if inst == installation_id and not dl.retried]

    def count(self, installation_id: str) -> int:
        return sum(1 for (inst, _) in self._letters if inst == installation_id)

    def purge(self, installation_id: str) -> int:
        to_remove = [k for k in self._letters if k[0] == installation_id and self._letters[k].retried]
        for k in to_remove:
            del self._letters[k]
        return len(to_remove)

    def _get(self, installation_id: str, letter_id: str) -> DeadLetter:
        key = (installation_id, letter_id)
        dl = self._letters.get(key)
        if dl is None:
            raise KeyError(f"Dead letter {letter_id} not found")
        return dl
