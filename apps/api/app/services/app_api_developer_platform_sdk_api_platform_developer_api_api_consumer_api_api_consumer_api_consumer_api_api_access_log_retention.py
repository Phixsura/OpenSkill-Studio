"""Consumer API Access Log Retention — manage access log lifecycle per consumer."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import structlog

log = structlog.get_logger()

@dataclass
class AccessLogEntry:
    log_id: str
    consumer_id: str
    method: str
    path: str
    status_code: int
    ip_address: str = ""
    timestamp: datetime | None = None

@dataclass
class RetentionConfig:
    consumer_id: str
    retention_days: int = 90
    max_entries: int = 100000
    archive_enabled: bool = True

@dataclass
class RetentionStats:
    total_entries: int
    oldest_entry_age_days: int
    storage_estimate_mb: float
    entries_due_for_deletion: int

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiAccessLogRetention:
    def __init__(self) -> None:
        self._configs: dict[tuple[str, str], RetentionConfig] = {}
        self._logs: dict[tuple[str, str], list[AccessLogEntry]] = {}

    def set_config(self, installation_id: str, config: RetentionConfig) -> RetentionConfig:
        if not installation_id:
            raise ValueError("installation_id is required")
        if config.retention_days < 1:
            raise ValueError("retention_days must be positive")
        self._configs[(installation_id, config.consumer_id)] = config
        return config

    def append(self, installation_id: str, entry: AccessLogEntry) -> AccessLogEntry:
        entry.timestamp = entry.timestamp or datetime.utcnow()
        key = (installation_id, entry.consumer_id)
        config = self._configs.get(key, RetentionConfig(consumer_id=entry.consumer_id))
        if key not in self._logs:
            self._logs[key] = []
        self._logs[key].append(entry)
        if len(self._logs[key]) > config.max_entries:
            self._logs[key] = self._logs[key][-config.max_entries:]
        return entry

    def query(self, installation_id: str, consumer_id: str, method: str | None = None, status_code: int | None = None, limit: int = 50) -> list[AccessLogEntry]:
        logs = self._logs.get((installation_id, consumer_id), [])
        if method:
            logs = [l for l in logs if l.method == method]
        if status_code is not None:
            logs = [l for l in logs if l.status_code == status_code]
        return list(reversed(logs[-limit:]))

    def cleanup(self, installation_id: str, consumer_id: str, now: datetime) -> int:
        key = (installation_id, consumer_id)
        config = self._configs.get(key, RetentionConfig(consumer_id=consumer_id))
        logs = self._logs.get(key, [])
        cutoff = now - timedelta(days=config.retention_days)
        before = len(logs)
        self._logs[key] = [l for l in logs if l.timestamp and l.timestamp >= cutoff]
        return before - len(self._logs[key])

    def get_stats(self, installation_id: str, consumer_id: str, now: datetime) -> RetentionStats:
        key = (installation_id, consumer_id)
        config = self._configs.get(key, RetentionConfig(consumer_id=consumer_id))
        logs = self._logs.get(key, [])
        if not logs:
            return RetentionStats(total_entries=0, oldest_entry_age_days=0, storage_estimate_mb=0, entries_due_for_deletion=0)
        oldest_age = (now - (logs[0].timestamp or now)).days
        cutoff = now - timedelta(days=config.retention_days)
        due = sum(1 for l in logs if l.timestamp and l.timestamp < cutoff)
        size_mb = round(len(logs) * 0.0005, 2)  # ~500 bytes per entry
        return RetentionStats(total_entries=len(logs), oldest_entry_age_days=oldest_age, storage_estimate_mb=size_mb, entries_due_for_deletion=due)
