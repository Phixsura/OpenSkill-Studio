"""Consumer API Webhook Monitoring — real-time webhook health monitoring."""
from __future__ import annotations

import statistics
import structlog
from dataclasses import dataclass, field

logger = structlog.get_logger()


@dataclass
class WebhookPing:
    webhook_id: str
    timestamp: float
    success: bool
    latency_ms: float
    status_code: int = 200


@dataclass
class WebhookMonitor:
    """Real-time webhook health monitoring with alerting."""

    _pings: dict[str, list[WebhookPing]] = field(default_factory=dict)
    _alert_threshold: int = 3  # consecutive failures to alert
    _max_pings: int = 1000

    def configure(self, alert_threshold: int = 3) -> dict:
        if alert_threshold < 1:
            raise ValueError("alert_threshold must be positive")
        self._alert_threshold = alert_threshold
        return {"alert_threshold": alert_threshold}

    def ping(self, ping: WebhookPing) -> dict:
        pings = self._pings.setdefault(ping.webhook_id, [])
        if len(pings) >= self._max_pings:
            self._pings[ping.webhook_id] = pings[-(self._max_pings // 2):]
        self._pings[ping.webhook_id].append(ping)
        # Check consecutive failures
        recent = self._pings[ping.webhook_id][-self._alert_threshold:]
        consecutive_failures = all(not p.success for p in recent) and len(recent) >= self._alert_threshold
        result = {"webhook_id": ping.webhook_id, "success": ping.success,
                  "latency_ms": ping.latency_ms}
        if consecutive_failures:
            result["alert"] = True
            result["alert_reason"] = f"{self._alert_threshold} consecutive failures"
            logger.warning("webhook_alert", webhook_id=ping.webhook_id)
        return result

    def get_health(self, webhook_id: str) -> dict:
        pings = self._pings.get(webhook_id, [])
        if not pings:
            return {"webhook_id": webhook_id, "status": "unknown"}
        recent = pings[-20:]
        success_count = sum(1 for p in recent if p.success)
        success_rate = round(success_count / len(recent) * 100, 1)
        latencies = [p.latency_ms for p in recent if p.success]
        avg_latency = round(statistics.mean(latencies), 2) if latencies else 0
        if success_rate >= 99:
            status = "healthy"
        elif success_rate >= 90:
            status = "degraded"
        else:
            status = "unhealthy"
        return {
            "webhook_id": webhook_id, "status": status,
            "success_rate": success_rate, "avg_latency_ms": avg_latency,
            "total_pings": len(pings), "recent_pings": len(recent),
        }

    def get_all_health(self) -> list[dict]:
        results = [self.get_health(wid) for wid in self._pings]
        results.sort(key=lambda x: x.get("success_rate", 0))
        return results

    def get_timeline(self, webhook_id: str, limit: int = 20) -> list[dict]:
        pings = self._pings.get(webhook_id, [])
        return [
            {"timestamp": p.timestamp, "success": p.success,
             "latency_ms": p.latency_ms, "status_code": p.status_code}
            for p in list(reversed(pings))[:limit]
        ]

    def get_stats(self) -> dict:
        total_pings = sum(len(v) for v in self._pings.values())
        total_success = sum(sum(1 for p in v if p.success) for v in self._pings.values())
        return {
            "webhooks_monitored": len(self._pings),
            "total_pings": total_pings,
            "overall_success_rate": round(total_success / total_pings * 100, 1) if total_pings > 0 else 0,
        }
