"""App Log Retention — manage log retention policies and cleanup.

Manages log retention for installed apps:
- Define retention policies per log type
- Track storage usage per policy
- Cleanup expired logs
- Per-installation scoped policies
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class RetentionPolicy:
    """A log retention policy."""

    policy_id: str
    log_type: str  # "access", "error", "audit", "debug"
    retention_days: int
    max_size_mb: float = 0  # 0 = unlimited
    current_size_mb: float = 0
    entry_count: int = 0
    last_cleanup_at: float | None = None


class AppLogRetention:
    """Manage log retention policies and cleanup."""

    def __init__(self) -> None:
        self._policies: dict[tuple[str, str], RetentionPolicy] = {}

    def create_policy(
        self,
        installation_id: str,
        policy_id: str,
        log_type: str,
        retention_days: int,
        max_size_mb: float = 0,
    ) -> RetentionPolicy:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not policy_id:
            raise ValueError("policy_id is required")
        if retention_days < 1:
            raise ValueError("retention_days must be >= 1")

        key = (installation_id, policy_id)
        if key in self._policies:
            raise ValueError(f"Policy {policy_id} already exists")

        policy = RetentionPolicy(
            policy_id=policy_id, log_type=log_type,
            retention_days=retention_days, max_size_mb=max_size_mb,
        )
        self._policies[key] = policy
        return policy

    def update_usage(
        self,
        installation_id: str,
        policy_id: str,
        size_mb: float,
        entry_count: int,
    ) -> RetentionPolicy:
        policy = self._get(installation_id, policy_id)
        policy.current_size_mb = max(0, size_mb)
        policy.entry_count = max(0, entry_count)
        return policy

    def needs_cleanup(self, installation_id: str, policy_id: str) -> bool:
        policy = self._get(installation_id, policy_id)
        if policy.max_size_mb > 0 and policy.current_size_mb > policy.max_size_mb:
            return True
        return False

    def record_cleanup(
        self,
        installation_id: str,
        policy_id: str,
        removed_entries: int,
        freed_mb: float,
        now: float | None = None,
    ) -> RetentionPolicy:
        policy = self._get(installation_id, policy_id)
        policy.entry_count = max(0, policy.entry_count - removed_entries)
        policy.current_size_mb = max(0, policy.current_size_mb - freed_mb)
        policy.last_cleanup_at = now or time.time()
        return policy

    def get_policy(self, installation_id: str, policy_id: str) -> RetentionPolicy:
        return self._get(installation_id, policy_id)

    def list_policies(self, installation_id: str) -> list[RetentionPolicy]:
        return [p for (inst, _), p in self._policies.items() if inst == installation_id]

    def total_size_mb(self, installation_id: str) -> float:
        return sum(p.current_size_mb for (inst, _), p in self._policies.items() if inst == installation_id)

    def _get(self, installation_id: str, policy_id: str) -> RetentionPolicy:
        key = (installation_id, policy_id)
        p = self._policies.get(key)
        if p is None:
            raise KeyError(f"Policy {policy_id} not found")
        return p
