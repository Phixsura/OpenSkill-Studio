"""Webhook replay queue — store and replay failed webhook deliveries."""
from __future__ import annotations
import secrets


class WebhookReplayQueue:
    def __init__(self):
        self._queue: list[dict] = []

    def enqueue(self, *, url: str, payload: dict, status_code: int,
                error: str = "") -> dict:
        entry = {"id": f"wr_{secrets.token_hex(6)}", "url": url, "payload": payload,
                 "original_status": status_code, "error": error,
                 "replay_count": 0, "last_replay_status": None}
        self._queue.append(entry)
        return {"id": entry["id"], "queued": True, "queue_size": len(self._queue)}

    def replay(self, entry_id: str, *, success: bool, status_code: int = 200) -> dict:
        entry = next((e for e in self._queue if e["id"] == entry_id), None)
        if not entry:
            return {"error": "Entry not found"}
        entry["replay_count"] += 1
        entry["last_replay_status"] = status_code
        if success:
            self._queue.remove(entry)
            return {"replayed": True, "success": True, "removed": True}
        return {"replayed": True, "success": False, "retry": entry["replay_count"]}

    def list_queue(self) -> list[dict]:
        return [{"id": e["id"], "url": e["url"], "original_status": e["original_status"],
                 "replay_count": e["replay_count"], "error": e["error"]}
                for e in self._queue]

    def stats(self) -> dict:
        return {"queue_size": len(self._queue),
                "total_retries": sum(e["replay_count"] for e in self._queue)}
