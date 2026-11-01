"""Quota Enforcement — enforce resource quotas for extension sandboxes.

Tracks resource consumption (storage, compute, API calls, bandwidth)
against allocated quotas with soft/hard limits and overage handling.
"""
from __future__ import annotations
import secrets
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum


class ResourceType(str, Enum):
    STORAGE_MB = "storage_mb"
    COMPUTE_SECONDS = "compute_seconds"
    API_CALLS = "api_calls"
    BANDWIDTH_MB = "bandwidth_mb"
    CONCURRENT_CONNECTIONS = "concurrent_connections"


class QuotaState(str, Enum):
    OK = "ok"
    WARNING = "warning"  # above soft limit
    EXCEEDED = "exceeded"  # above hard limit
    BLOCKED = "blocked"


@dataclass
class ResourceQuota:
    resource_type: ResourceType
    soft_limit: float  # warning threshold
    hard_limit: float  # block threshold
    current_usage: float = 0.0

    @property
    def usage_percent(self) -> float:
        return round(self.current_usage / self.hard_limit * 100, 1) if self.hard_limit else 0

    @property
    def state(self) -> QuotaState:
        if self.current_usage >= self.hard_limit:
            return QuotaState.EXCEEDED
        if self.current_usage >= self.soft_limit:
            return QuotaState.WARNING
        return QuotaState.OK


class QuotaEnforcementService:
    """Enforces resource quotas with soft and hard limits."""

    def __init__(self):
        self._quotas: dict[str, dict[ResourceType, ResourceQuota]] = defaultdict(dict)

    def set_quota(self, extension_id: str, resource: ResourceType,
                  soft_limit: float, hard_limit: float) -> ResourceQuota:
        if soft_limit > hard_limit:
            raise ValueError("Soft limit must be <= hard limit")
        if hard_limit <= 0:
            raise ValueError("Hard limit must be positive")
        quota = ResourceQuota(
            resource_type=resource, soft_limit=soft_limit,
            hard_limit=hard_limit,
        )
        self._quotas[extension_id][resource] = quota
        return quota

    def consume(self, extension_id: str, resource: ResourceType,
                amount: float) -> dict:
        quota = self._quotas.get(extension_id, {}).get(resource)
        if not quota:
            return {"allowed": True, "reason": "No quota set"}
        if amount <= 0:
            return {"allowed": False, "reason": "Amount must be positive"}

        new_usage = quota.current_usage + amount
        if new_usage > quota.hard_limit:
            return {
                "allowed": False, "reason": "Hard limit exceeded",
                "current": quota.current_usage, "limit": quota.hard_limit,
                "requested": amount,
            }

        quota.current_usage = new_usage
        state = quota.state
        return {
            "allowed": True, "state": state.value,
            "current": quota.current_usage,
            "remaining": round(quota.hard_limit - quota.current_usage, 2),
            "warning": state == QuotaState.WARNING,
        }

    def release(self, extension_id: str, resource: ResourceType,
                amount: float) -> bool:
        quota = self._quotas.get(extension_id, {}).get(resource)
        if not quota:
            return False
        quota.current_usage = max(0, quota.current_usage - amount)
        return True

    def check(self, extension_id: str, resource: ResourceType) -> dict:
        quota = self._quotas.get(extension_id, {}).get(resource)
        if not quota:
            return {"exists": False}
        return {
            "exists": True, "state": quota.state.value,
            "current": quota.current_usage,
            "soft_limit": quota.soft_limit,
            "hard_limit": quota.hard_limit,
            "usage_percent": quota.usage_percent,
        }

    def get_all_quotas(self, extension_id: str) -> list[dict]:
        quotas = self._quotas.get(extension_id, {})
        return [
            {
                "resource": rt.value, "state": q.state.value,
                "current": q.current_usage,
                "soft_limit": q.soft_limit, "hard_limit": q.hard_limit,
                "usage_percent": q.usage_percent,
            }
            for rt, q in quotas.items()
        ]

    def reset(self, extension_id: str, resource: ResourceType) -> bool:
        quota = self._quotas.get(extension_id, {}).get(resource)
        if quota:
            quota.current_usage = 0
            return True
        return False
