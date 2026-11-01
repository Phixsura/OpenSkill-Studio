"""Endpoint Access Log — structured access logging with search and retention."""
from __future__ import annotations

import structlog
from dataclasses import dataclass, field

logger = structlog.get_logger()


@dataclass
class AccessEntry:
    request_id: str
    timestamp: str
    consumer_id: str
    endpoint_id: str
    method: str
    status_code: int
    latency_ms: float
    ip_address: str = ""
    user_agent: str = ""
    request_size: int = 0
    response_size: int = 0


@dataclass
class AccessLog:
    """Structured access log with search and aggregation."""

    _entries: list[AccessEntry] = field(default_factory=list)
    _max_entries: int = 100000

    def log(self, entry: AccessEntry) -> dict:
        if len(self._entries) >= self._max_entries:
            self._entries = self._entries[-(self._max_entries // 2):]
        self._entries.append(entry)
        return {"request_id": entry.request_id, "logged": True,
                "total_entries": len(self._entries)}

    def search(self, consumer_id: str | None = None, endpoint_id: str | None = None,
               method: str | None = None, status_min: int | None = None,
               status_max: int | None = None, limit: int = 50) -> list[dict]:
        results = []
        for entry in reversed(self._entries):
            if consumer_id and entry.consumer_id != consumer_id:
                continue
            if endpoint_id and entry.endpoint_id != endpoint_id:
                continue
            if method and entry.method != method.upper():
                continue
            if status_min is not None and entry.status_code < status_min:
                continue
            if status_max is not None and entry.status_code > status_max:
                continue
            results.append({
                "request_id": entry.request_id,
                "timestamp": entry.timestamp,
                "consumer_id": entry.consumer_id,
                "endpoint_id": entry.endpoint_id,
                "method": entry.method,
                "status_code": entry.status_code,
                "latency_ms": entry.latency_ms,
            })
            if len(results) >= limit:
                break
        return results

    def get_summary(self, endpoint_id: str | None = None) -> dict:
        entries = self._entries
        if endpoint_id:
            entries = [e for e in entries if e.endpoint_id == endpoint_id]
        if not entries:
            return {"total": 0}
        total = len(entries)
        success = sum(1 for e in entries if 200 <= e.status_code < 300)
        client_err = sum(1 for e in entries if 400 <= e.status_code < 500)
        server_err = sum(1 for e in entries if e.status_code >= 500)
        avg_latency = sum(e.latency_ms for e in entries) / total
        total_req_size = sum(e.request_size for e in entries)
        total_resp_size = sum(e.response_size for e in entries)
        return {
            "total": total,
            "success": success,
            "client_errors": client_err,
            "server_errors": server_err,
            "success_rate": round(success / total * 100, 1),
            "avg_latency_ms": round(avg_latency, 2),
            "total_request_bytes": total_req_size,
            "total_response_bytes": total_resp_size,
        }

    def get_top_consumers(self, limit: int = 10) -> list[dict]:
        counts: dict[str, int] = {}
        for e in self._entries:
            counts[e.consumer_id] = counts.get(e.consumer_id, 0) + 1
        ranked = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:limit]
        return [{"consumer_id": c, "request_count": n} for c, n in ranked]

    def get_error_entries(self, limit: int = 20) -> list[dict]:
        return self.search(status_min=400, limit=limit)

    def count(self) -> int:
        return len(self._entries)
