"""Consumer Webhook Dashboard — webhook health overview with delivery metrics."""
from __future__ import annotations

import statistics
import structlog
from dataclasses import dataclass, field

logger = structlog.get_logger()


@dataclass
class DeliveryEvent:
    webhook_id: str
    timestamp: str
    status_code: int
    latency_ms: float
    payload_size: int = 0
    retry_count: int = 0


@dataclass
class WebhookDashboard:
    """Aggregate webhook delivery metrics for dashboard display."""

    _events: dict[str, list[DeliveryEvent]] = field(default_factory=dict)

    def record(self, event: DeliveryEvent) -> dict:
        self._events.setdefault(event.webhook_id, []).append(event)
        return {"webhook_id": event.webhook_id,
                "total_events": len(self._events[event.webhook_id])}

    def get_webhook_health(self, webhook_id: str) -> dict:
        events = self._events.get(webhook_id, [])
        if not events:
            return {"webhook_id": webhook_id, "status": "no_data"}
        total = len(events)
        successful = sum(1 for e in events if 200 <= e.status_code < 300)
        failed = total - successful
        success_rate = round(successful / total * 100, 1)
        latencies = [e.latency_ms for e in events]
        avg_latency = round(statistics.mean(latencies), 2)
        retries = sum(e.retry_count for e in events)
        if success_rate >= 99:
            health = "healthy"
        elif success_rate >= 90:
            health = "degraded"
        else:
            health = "critical"
        return {
            "webhook_id": webhook_id,
            "health": health,
            "total_deliveries": total,
            "successful": successful,
            "failed": failed,
            "success_rate": success_rate,
            "avg_latency_ms": avg_latency,
            "total_retries": retries,
        }

    def get_overview(self) -> dict:
        all_webhooks = list(self._events.keys())
        if not all_webhooks:
            return {"total_webhooks": 0}
        healths = [self.get_webhook_health(wid) for wid in all_webhooks]
        healthy = sum(1 for h in healths if h.get("health") == "healthy")
        degraded = sum(1 for h in healths if h.get("health") == "degraded")
        critical = sum(1 for h in healths if h.get("health") == "critical")
        total_deliveries = sum(h.get("total_deliveries", 0) for h in healths)
        total_failed = sum(h.get("failed", 0) for h in healths)
        return {
            "total_webhooks": len(all_webhooks),
            "healthy": healthy,
            "degraded": degraded,
            "critical": critical,
            "total_deliveries": total_deliveries,
            "total_failed": total_failed,
            "overall_success_rate": round(
                (total_deliveries - total_failed) / total_deliveries * 100, 1
            ) if total_deliveries > 0 else 0,
        }

    def get_top_failures(self, limit: int = 5) -> list[dict]:
        results = []
        for wid in self._events:
            health = self.get_webhook_health(wid)
            if health.get("failed", 0) > 0:
                results.append(health)
        results.sort(key=lambda x: x.get("failed", 0), reverse=True)
        return results[:limit]

    def get_latency_ranking(self, limit: int = 10) -> list[dict]:
        results = []
        for wid in self._events:
            health = self.get_webhook_health(wid)
            if health.get("status") != "no_data":
                results.append({"webhook_id": wid,
                                "avg_latency_ms": health["avg_latency_ms"]})
        results.sort(key=lambda x: x["avg_latency_ms"], reverse=True)
        return results[:limit]
