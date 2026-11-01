"""App Data Retention — manage data lifecycle policies.

Manages data retention:
- Define retention policies per data type
- Track data age and scheduled purge dates
- Enforce retention limits
- Per-installation scoped policies
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class RetentionPolicy:
    """A data retention policy."""

    policy_id: str
    data_type: str  # "logs", "events", "sessions", "backups"
    retention_days: int
    action: str = "delete"  # "delete", "archive", "anonymize"
    enabled: bool = True


@dataclass
class RetentionRecord:
    """A record subject to retention."""

    record_id: str
    data_type: str
    created_at: float
    purge_at: float
    purged: bool = False


class AppDataRetention:
    """Manage data lifecycle policies."""

    def __init__(self) -> None:
        self._policies: dict[tuple[str, str], RetentionPolicy] = {}
        self._records: dict[str, list[RetentionRecord]] = {}

    def set_policy(
        self, installation_id: str, policy_id: str, data_type: str,
        retention_days: int, action: str = "delete",
    ) -> RetentionPolicy:
        if not installation_id:
            raise ValueError("installation_id is required")
        if retention_days < 1:
            raise ValueError("retention_days must be at least 1")
        if action not in ("delete", "archive", "anonymize"):
            raise ValueError("action must be delete, archive, or anonymize")

        policy = RetentionPolicy(
            policy_id=policy_id, data_type=data_type,
            retention_days=retention_days, action=action,
        )
        self._policies[(installation_id, policy_id)] = policy
        return policy

    def add_record(
        self, installation_id: str, record_id: str, data_type: str,
    ) -> RetentionRecord:
        policy = self._find_policy(installation_id, data_type)
        if policy is None:
            raise ValueError(f"No retention policy for {data_type}")

        now = time.time()
        purge_at = now + (policy.retention_days * 86400)

        record = RetentionRecord(
            record_id=record_id, data_type=data_type,
            created_at=now, purge_at=purge_at,
        )
        self._records.setdefault(installation_id, []).append(record)
        return record

    def due_for_purge(self, installation_id: str) -> list[RetentionRecord]:
        """Records past their purge date."""
        now = time.time()
        return [
            r for r in self._records.get(installation_id, [])
            if r.purge_at <= now and not r.purged
        ]

    def purge(self, installation_id: str, record_id: str) -> RetentionRecord:
        for r in self._records.get(installation_id, []):
            if r.record_id == record_id:
                r.purged = True
                return r
        raise KeyError(f"Record {record_id} not found")

    def list_policies(self, installation_id: str) -> list[RetentionPolicy]:
        return [p for (inst, _), p in self._policies.items() if inst == installation_id]

    def _find_policy(self, installation_id: str, data_type: str) -> RetentionPolicy | None:
        for (inst, _), p in self._policies.items():
            if inst == installation_id and p.data_type == data_type and p.enabled:
                return p
        return None
