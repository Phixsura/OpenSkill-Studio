"""Consumer API Key Usage Monitor — real-time API key usage monitoring."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import structlog

log = structlog.get_logger()

@dataclass
class KeyUsageSnapshot:
    key_id: str
    requests_last_minute: int = 0
    requests_last_hour: int = 0
    errors_last_hour: int = 0
    avg_latency_ms: float = 0.0
    last_used_at: datetime | None = None
    status: str = "active"  # "active", "idle", "throttled"

@dataclass
class KeyUsageAlert:
    key_id: str
    alert_type: str  # "high_usage", "high_errors", "idle", "throttled"
    message: str
    timestamp: datetime

class AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiKeyUsageMonitor:
    def __init__(self) -> None:
        self._usage: dict[tuple[str, str, str], list[tuple[datetime, bool, float]]] = {}  # (inst, consumer, key) -> [(ts, is_error, latency)]
        self._alerts: dict[tuple[str, str], list[KeyUsageAlert]] = {}

    def record(self, installation_id: str, consumer_id: str, key_id: str, is_error: bool, latency_ms: float, now: datetime) -> None:
        if not installation_id:
            raise ValueError("installation_id is required")
        key = (installation_id, consumer_id, key_id)
        if key not in self._usage:
            self._usage[key] = []
        self._usage[key].append((now, is_error, latency_ms))
        if len(self._usage[key]) > 10000:
            self._usage[key] = self._usage[key][-10000:]

    def get_snapshot(self, installation_id: str, consumer_id: str, key_id: str, now: datetime) -> KeyUsageSnapshot:
        records = self._usage.get((installation_id, consumer_id, key_id), [])
        if not records:
            return KeyUsageSnapshot(key_id=key_id, status="idle")
        minute_ago = now - timedelta(minutes=1)
        hour_ago = now - timedelta(hours=1)
        last_min = [r for r in records if r[0] >= minute_ago]
        last_hour = [r for r in records if r[0] >= hour_ago]
        errors = sum(1 for r in last_hour if r[1])
        latencies = [r[2] for r in last_hour if not r[1]]
        avg_lat = sum(latencies) / len(latencies) if latencies else 0
        status = "active"
        if not last_min:
            status = "idle"
        elif len(last_min) > 50:
            status = "throttled"
        return KeyUsageSnapshot(key_id=key_id, requests_last_minute=len(last_min), requests_last_hour=len(last_hour), errors_last_hour=errors, avg_latency_ms=round(avg_lat, 1), last_used_at=records[-1][0], status=status)

    def check_alerts(self, installation_id: str, consumer_id: str, key_id: str, now: datetime) -> list[KeyUsageAlert]:
        snapshot = self.get_snapshot(installation_id, consumer_id, key_id, now)
        alerts: list[KeyUsageAlert] = []
        if snapshot.requests_last_minute > 30:
            alerts.append(KeyUsageAlert(key_id=key_id, alert_type="high_usage", message=f"{snapshot.requests_last_minute} req/min", timestamp=now))
        if snapshot.errors_last_hour > 10:
            alerts.append(KeyUsageAlert(key_id=key_id, alert_type="high_errors", message=f"{snapshot.errors_last_hour} errors/hour", timestamp=now))
        akey = (installation_id, consumer_id)
        if akey not in self._alerts:
            self._alerts[akey] = []
        self._alerts[akey].extend(alerts)
        return alerts

    def get_all_snapshots(self, installation_id: str, consumer_id: str, now: datetime) -> list[KeyUsageSnapshot]:
        keys = {kid for (inst, cid, kid) in self._usage if inst == installation_id and cid == consumer_id}
        return sorted([self.get_snapshot(installation_id, consumer_id, kid, now) for kid in keys], key=lambda s: -s.requests_last_hour)
