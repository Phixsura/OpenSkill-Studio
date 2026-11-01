"""Consumer API Resource Quota — manage per-resource quotas."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class ResourceQuota:
    resource_type: str  # "webhooks", "api_keys", "endpoints", "team_members"
    consumer_id: str
    max_count: int
    current_count: int = 0

@dataclass
class QuotaCheckResult:
    resource_type: str
    allowed: bool
    current: int
    max: int
    remaining: int

VALID_RESOURCES = {"webhooks", "api_keys", "endpoints", "team_members", "sandboxes", "oauth_clients", "custom_fields"}

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiResourceQuota:
    def __init__(self) -> None:
        self._quotas: dict[tuple[str, str, str], ResourceQuota] = {}  # (inst, consumer, resource)

    def set_quota(self, installation_id: str, quota: ResourceQuota) -> ResourceQuota:
        if not installation_id:
            raise ValueError("installation_id is required")
        if quota.resource_type not in VALID_RESOURCES:
            raise ValueError(f"Invalid resource_type: {quota.resource_type}")
        if quota.max_count < 0:
            raise ValueError("max_count must be non-negative")
        self._quotas[(installation_id, quota.consumer_id, quota.resource_type)] = quota
        return quota

    def check(self, installation_id: str, consumer_id: str, resource_type: str) -> QuotaCheckResult:
        key = (installation_id, consumer_id, resource_type)
        quota = self._quotas.get(key)
        if not quota:
            return QuotaCheckResult(resource_type=resource_type, allowed=True, current=0, max=0, remaining=0)
        remaining = max(0, quota.max_count - quota.current_count)
        return QuotaCheckResult(resource_type=resource_type, allowed=remaining > 0, current=quota.current_count, max=quota.max_count, remaining=remaining)

    def consume(self, installation_id: str, consumer_id: str, resource_type: str) -> QuotaCheckResult:
        key = (installation_id, consumer_id, resource_type)
        quota = self._quotas.get(key)
        if not quota:
            return QuotaCheckResult(resource_type=resource_type, allowed=True, current=0, max=0, remaining=0)
        if quota.current_count >= quota.max_count:
            return QuotaCheckResult(resource_type=resource_type, allowed=False, current=quota.current_count, max=quota.max_count, remaining=0)
        quota.current_count += 1
        remaining = quota.max_count - quota.current_count
        return QuotaCheckResult(resource_type=resource_type, allowed=True, current=quota.current_count, max=quota.max_count, remaining=remaining)

    def release(self, installation_id: str, consumer_id: str, resource_type: str) -> None:
        key = (installation_id, consumer_id, resource_type)
        quota = self._quotas.get(key)
        if quota and quota.current_count > 0:
            quota.current_count -= 1

    def list_quotas(self, installation_id: str, consumer_id: str) -> list[ResourceQuota]:
        return [q for (inst, cid, _), q in self._quotas.items() if inst == installation_id and cid == consumer_id]
