"""Consumer API Webhook Dead Letter Inspector — inspect and replay dead letters."""
from __future__ import annotations

import structlog
from dataclasses import dataclass, field

logger = structlog.get_logger()


@dataclass
class DeadLetter:
    letter_id: str
    webhook_id: str
    event_type: str
    payload: dict
    error: str
    failed_at: str
    attempts: int = 1
    status: str = "dead"  # dead, replayed, discarded


@dataclass
class DeadLetterInspector:
    """Inspect and manage dead letter webhook events."""

    _letters: dict[str, DeadLetter] = field(default_factory=dict)

    def add(self, letter: DeadLetter) -> dict:
        if letter.letter_id in self._letters:
            raise ValueError(f"Dead letter {letter.letter_id} already exists")
        self._letters[letter.letter_id] = letter
        logger.info("dead_letter_added", letter_id=letter.letter_id)
        return {"letter_id": letter.letter_id, "webhook_id": letter.webhook_id}

    def inspect(self, letter_id: str) -> dict | None:
        dl = self._letters.get(letter_id)
        if not dl:
            return None
        return {
            "letter_id": dl.letter_id, "webhook_id": dl.webhook_id,
            "event_type": dl.event_type, "payload": dl.payload,
            "error": dl.error, "failed_at": dl.failed_at,
            "attempts": dl.attempts, "status": dl.status,
        }

    def replay(self, letter_id: str, success: bool = True) -> dict:
        dl = self._letters.get(letter_id)
        if not dl:
            raise ValueError(f"Dead letter {letter_id} not found")
        if dl.status != "dead":
            return {"replayed": False, "reason": f"status_is_{dl.status}"}
        dl.attempts += 1
        if success:
            dl.status = "replayed"
            logger.info("dead_letter_replayed", letter_id=letter_id)
            return {"replayed": True, "status": "replayed"}
        return {"replayed": False, "attempts": dl.attempts}

    def discard(self, letter_id: str) -> dict:
        dl = self._letters.get(letter_id)
        if not dl:
            return {"discarded": False}
        dl.status = "discarded"
        return {"discarded": True, "letter_id": letter_id}

    def replay_batch(self, letter_ids: list[str]) -> dict:
        replayed = 0
        failed = 0
        for lid in letter_ids:
            try:
                result = self.replay(lid)
                if result.get("replayed"):
                    replayed += 1
                else:
                    failed += 1
            except ValueError:
                failed += 1
        return {"replayed": replayed, "failed": failed, "total": len(letter_ids)}

    def list_dead(self, webhook_id: str | None = None, limit: int = 50) -> list[dict]:
        letters = [dl for dl in self._letters.values() if dl.status == "dead"]
        if webhook_id:
            letters = [dl for dl in letters if dl.webhook_id == webhook_id]
        return [
            {"letter_id": dl.letter_id, "webhook_id": dl.webhook_id,
             "event_type": dl.event_type, "error": dl.error, "attempts": dl.attempts}
            for dl in letters[:limit]
        ]

    def purge_discarded(self) -> dict:
        before = len(self._letters)
        self._letters = {k: v for k, v in self._letters.items() if v.status != "discarded"}
        return {"purged": before - len(self._letters)}

    def get_stats(self) -> dict:
        letters = list(self._letters.values())
        return {
            "total": len(letters),
            "dead": sum(1 for dl in letters if dl.status == "dead"),
            "replayed": sum(1 for dl in letters if dl.status == "replayed"),
            "discarded": sum(1 for dl in letters if dl.status == "discarded"),
        }
