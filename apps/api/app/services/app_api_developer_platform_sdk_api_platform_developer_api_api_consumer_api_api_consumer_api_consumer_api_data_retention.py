"""Consumer API Data Retention — manage data lifecycle and retention policies."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import structlog

log = structlog.get_logger()

@dataclass
class RetentionPolicy:
    policy_id: str
    data_type: str  # "logs", "events", "analytics", "exports", "sessions"
    retention_days: int
    archive_before_delete: bool = True
    auto_delete: bool = True

@dataclass
class RetentionRecord:
    data_type: str
    record_count: int
    oldest_at: datetime
    newest_at: datetime
    bytes_estimate: int = 0

@dataclass
class PurgeResult:
    data_type: str
    records_purged: int
    bytes_freed: int
    archived: bool

VALID_DATA_TYPES = {"logs", "events", "analytics", "exports", "sessions", "audit_trail", "metrics"}

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiDataRetention:
    def __init__(self) -> None:
        self._policies: dict[tuple[str, str, str], RetentionPolicy] = {}  # (inst, consumer, data_type)
        self._records: dict[tuple[str, str, str], RetentionRecord] = {}

    def set_policy(self, installation_id: str, consumer_id: str, policy: RetentionPolicy) -> RetentionPolicy:
        if not installation_id:
            raise ValueError("installation_id is required")
        if policy.data_type not in VALID_DATA_TYPES:
            raise ValueError(f"Invalid data_type: {policy.data_type}")
        if policy.retention_days < 1:
            raise ValueError("retention_days must be positive")
        self._policies[(installation_id, consumer_id, policy.data_type)] = policy
        return policy

    def record_data(self, installation_id: str, consumer_id: str, record: RetentionRecord) -> RetentionRecord:
        self._records[(installation_id, consumer_id, record.data_type)] = record
        return record

    def check_expired(self, installation_id: str, consumer_id: str, now: datetime) -> list[tuple[RetentionPolicy, RetentionRecord]]:
        expired = []
        for (inst, cid, dt), policy in self._policies.items():
            if inst != installation_id or cid != consumer_id:
                continue
            record = self._records.get((inst, cid, dt))
            if not record:
                continue
            cutoff = now - timedelta(days=policy.retention_days)
            if record.oldest_at < cutoff:
                expired.append((policy, record))
        return expired

    def purge(self, installation_id: str, consumer_id: str, data_type: str, now: datetime) -> PurgeResult:
        key = (installation_id, consumer_id, data_type)
        policy = self._policies.get(key)
        record = self._records.get(key)
        if not policy or not record:
            raise ValueError("No policy or data found")
        archived = policy.archive_before_delete
        result = PurgeResult(data_type=data_type, records_purged=record.record_count, bytes_freed=record.bytes_estimate, archived=archived)
        del self._records[key]
        log.info("data_purged", installation_id=installation_id, consumer=consumer_id, type=data_type, records=record.record_count)
        return result

    def get_policies(self, installation_id: str, consumer_id: str) -> list[RetentionPolicy]:
        return [p for (inst, cid, _), p in self._policies.items() if inst == installation_id and cid == consumer_id]
