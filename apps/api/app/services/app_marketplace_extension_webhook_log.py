"""Webhook Log — structured logging and search for webhook events.

Records inbound/outbound webhook events with payload capture, filtering
by status/type/endpoint, and retention policy management.
"""
from __future__ import annotations
import secrets
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class WebhookDirection(str, Enum):
    INBOUND = "inbound"
    OUTBOUND = "outbound"


class LogStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    REJECTED = "rejected"


@dataclass
class WebhookLogEntry:
    log_id: str
    extension_id: str
    direction: WebhookDirection
    event_type: str
    endpoint_url: str
    status: LogStatus
    status_code: int = 0
    payload_size_bytes: int = 0
    latency_ms: float = 0.0
    error_message: str = ""
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


class WebhookLogService:
    """Manages webhook event logging with search and retention."""

    MAX_ENTRIES = 10000

    def __init__(self):
        self._entries: list[WebhookLogEntry] = []

    def log(self, extension_id: str, direction: WebhookDirection,
            event_type: str, endpoint_url: str, status: LogStatus,
            status_code: int = 0, payload_size_bytes: int = 0,
            latency_ms: float = 0.0, error_message: str = "") -> WebhookLogEntry:
        entry = WebhookLogEntry(
            log_id=f"wl_{secrets.token_urlsafe(10)}",
            extension_id=extension_id, direction=direction,
            event_type=event_type, endpoint_url=endpoint_url,
            status=status, status_code=status_code,
            payload_size_bytes=payload_size_bytes,
            latency_ms=latency_ms, error_message=error_message,
        )
        self._entries.append(entry)
        if len(self._entries) > self.MAX_ENTRIES:
            self._entries = self._entries[-self.MAX_ENTRIES:]
        return entry

    def search(self, extension_id: str, direction: WebhookDirection | None = None,
               status: LogStatus | None = None, event_type: str | None = None,
               limit: int = 50) -> list[WebhookLogEntry]:
        results = [e for e in self._entries if e.extension_id == extension_id]
        if direction:
            results = [e for e in results if e.direction == direction]
        if status:
            results = [e for e in results if e.status == status]
        if event_type:
            results = [e for e in results if e.event_type == event_type]
        return results[-limit:]

    def get_stats(self, extension_id: str) -> dict:
        entries = [e for e in self._entries if e.extension_id == extension_id]
        by_status: dict[str, int] = defaultdict(int)
        total_latency = 0.0
        for e in entries:
            by_status[e.status.value] += 1
            total_latency += e.latency_ms
        avg_latency = round(total_latency / len(entries), 2) if entries else 0
        return {
            "total": len(entries), "by_status": dict(by_status),
            "avg_latency_ms": avg_latency,
            "success_rate": round(by_status.get("success", 0) / max(len(entries), 1) * 100, 1),
        }

    def get_error_summary(self, extension_id: str) -> list[dict]:
        errors: dict[str, int] = defaultdict(int)
        for e in self._entries:
            if e.extension_id == extension_id and e.status != LogStatus.SUCCESS:
                key = e.error_message or f"HTTP {e.status_code}"
                errors[key] += 1
        return [{"error": k, "count": v} for k, v in sorted(errors.items(), key=lambda x: -x[1])]

    def purge(self, extension_id: str) -> int:
        before = len(self._entries)
        self._entries = [e for e in self._entries if e.extension_id != extension_id]
        return before - len(self._entries)
