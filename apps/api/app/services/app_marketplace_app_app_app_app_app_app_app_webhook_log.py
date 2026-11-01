"""Webhook delivery log — track webhook delivery attempts with full audit trail."""
from __future__ import annotations
import secrets


class WebhookDeliveryLog:
    def __init__(self):
        self._entries: list[dict] = []

    def log_delivery(self, *, webhook_id: str, url: str, event_type: str,
                      status_code: int, duration_ms: int, success: bool,
                      request_body: str = "", response_body: str = "") -> dict:
        entry_id = f"wdl_{secrets.token_hex(6)}"
        entry = {"id": entry_id, "webhook_id": webhook_id, "url": url,
                 "event_type": event_type, "status_code": status_code,
                 "duration_ms": duration_ms, "success": success,
                 "request_size": len(request_body), "response_size": len(response_body)}
        self._entries.append(entry)
        return {"id": entry_id, "logged": True}

    def query(self, *, webhook_id: str | None = None, success: bool | None = None,
               limit: int = 50) -> list[dict]:
        results = self._entries
        if webhook_id:
            results = [e for e in results if e["webhook_id"] == webhook_id]
        if success is not None:
            results = [e for e in results if e["success"] == success]
        return list(reversed(results[-limit:]))

    def stats(self, webhook_id: str | None = None) -> dict:
        entries = self._entries if not webhook_id else [e for e in self._entries if e["webhook_id"] == webhook_id]
        total = len(entries)
        successes = sum(1 for e in entries if e["success"])
        avg_duration = round(sum(e["duration_ms"] for e in entries) / max(total, 1), 1)
        return {"total_deliveries": total, "successes": successes,
                "failures": total - successes,
                "success_rate": round(successes / max(total, 1) * 100, 1),
                "avg_duration_ms": avg_duration}
