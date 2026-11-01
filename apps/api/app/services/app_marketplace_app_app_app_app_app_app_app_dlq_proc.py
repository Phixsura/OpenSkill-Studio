"""Dead letter queue processor — process and retry failed messages."""
from __future__ import annotations


class DlqProcessor:
    def __init__(self):
        self._messages: list[dict] = []
        self._reprocessed = 0
        self._discarded = 0

    def add(self, message_id: str, payload: dict, error: str, attempts: int) -> dict:
        self._messages.append({"id": message_id, "payload": payload,
                                "error": error, "attempts": attempts})
        return {"id": message_id, "queued": True, "dlq_size": len(self._messages)}

    def reprocess(self, message_id: str) -> dict:
        for i, m in enumerate(self._messages):
            if m["id"] == message_id:
                self._messages.pop(i)
                self._reprocessed += 1
                return {"id": message_id, "reprocessed": True}
        return {"id": message_id, "reprocessed": False}

    def discard(self, message_id: str) -> dict:
        for i, m in enumerate(self._messages):
            if m["id"] == message_id:
                self._messages.pop(i)
                self._discarded += 1
                return {"id": message_id, "discarded": True}
        return {"id": message_id, "discarded": False}

    def stats(self) -> dict:
        return {"pending": len(self._messages), "reprocessed": self._reprocessed,
                "discarded": self._discarded}
