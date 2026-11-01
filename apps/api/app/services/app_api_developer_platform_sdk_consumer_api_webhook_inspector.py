"""Consumer API Webhook Inspector — real-time webhook request/response inspection."""
from __future__ import annotations

import structlog
from dataclasses import dataclass, field
from datetime import datetime, timezone

logger = structlog.get_logger()


@dataclass
class InspectedRequest:
    request_id: str
    webhook_id: str
    method: str
    url: str
    headers: dict[str, str] = field(default_factory=dict)
    body: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class InspectedResponse:
    status_code: int
    headers: dict[str, str] = field(default_factory=dict)
    body: str = ""
    latency_ms: float = 0.0


@dataclass
class InspectionRecord:
    request: InspectedRequest
    response: InspectedResponse | None = None
    event_type: str = ""
    consumer_id: str = ""


@dataclass
class WebhookInspector:
    """Inspect webhook request/response pairs in real-time."""

    _records: list[InspectionRecord] = field(default_factory=list)
    _max_records: int = 1000

    def record(self, request: InspectedRequest, response: InspectedResponse | None = None,
               event_type: str = "", consumer_id: str = "") -> dict:
        if len(self._records) >= self._max_records:
            self._records = self._records[-(self._max_records // 2):]
        record = InspectionRecord(
            request=request, response=response,
            event_type=event_type, consumer_id=consumer_id,
        )
        self._records.append(record)
        logger.info("webhook_inspected", request_id=request.request_id)
        return {"request_id": request.request_id, "total": len(self._records)}

    def get_record(self, request_id: str) -> dict | None:
        for r in reversed(self._records):
            if r.request.request_id == request_id:
                result = {
                    "request_id": r.request.request_id,
                    "webhook_id": r.request.webhook_id,
                    "method": r.request.method,
                    "url": r.request.url,
                    "request_headers": r.request.headers,
                    "request_body": r.request.body,
                    "event_type": r.event_type,
                    "timestamp": r.request.timestamp,
                }
                if r.response:
                    result["response_status"] = r.response.status_code
                    result["response_headers"] = r.response.headers
                    result["response_body"] = r.response.body
                    result["latency_ms"] = r.response.latency_ms
                return result
        return None

    def list_recent(self, webhook_id: str | None = None, event_type: str | None = None,
                    limit: int = 20) -> list[dict]:
        records = list(reversed(self._records))
        if webhook_id:
            records = [r for r in records if r.request.webhook_id == webhook_id]
        if event_type:
            records = [r for r in records if r.event_type == event_type]
        return [
            {"request_id": r.request.request_id, "webhook_id": r.request.webhook_id,
             "event_type": r.event_type, "method": r.request.method,
             "status": r.response.status_code if r.response else None,
             "latency_ms": r.response.latency_ms if r.response else 0,
             "timestamp": r.request.timestamp}
            for r in records[:limit]
        ]

    def get_failed(self, limit: int = 20) -> list[dict]:
        failed = [r for r in reversed(self._records)
                  if r.response and r.response.status_code >= 400]
        return [
            {"request_id": r.request.request_id, "webhook_id": r.request.webhook_id,
             "status": r.response.status_code, "event_type": r.event_type}
            for r in failed[:limit]
        ]

    def get_stats(self) -> dict:
        total = len(self._records)
        with_response = sum(1 for r in self._records if r.response)
        failed = sum(1 for r in self._records if r.response and r.response.status_code >= 400)
        return {
            "total_inspected": total,
            "with_response": with_response,
            "failed": failed,
            "success_rate": round((with_response - failed) / with_response * 100, 1) if with_response > 0 else 0,
        }
