"""Usage Quota — track and enforce per-org extension usage quotas.

Manages quotas for API calls, storage, compute, and custom metrics
with threshold alerts and overage handling.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum


class QuotaType(str, Enum):
    API_CALLS = "api_calls"
    STORAGE_MB = "storage_mb"
    COMPUTE_SECONDS = "compute_seconds"
    WEBHOOKS = "webhooks"
    EXTENSIONS = "extensions"


class OveragePolicy(str, Enum):
    BLOCK = "block"
    ALLOW_WITH_CHARGE = "allow_with_charge"
    THROTTLE = "throttle"


@dataclass
class Quota:
    quota_type: QuotaType
    limit: int
    used: int = 0
    overage_policy: OveragePolicy = OveragePolicy.BLOCK
    alert_threshold: float = 0.8  # 80%

    @property
    def remaining(self) -> int:
        return max(0, self.limit - self.used)

    @property
    def usage_percent(self) -> float:
        return round(self.used / max(1, self.limit) * 100, 2)

    @property
    def over_limit(self) -> bool:
        return self.used >= self.limit

    @property
    def alert_triggered(self) -> bool:
        return self.usage_percent >= self.alert_threshold * 100


class UsageQuotaManager:
    """Manages per-org extension usage quotas."""

    def __init__(self):
        self._quotas: dict[str, dict[QuotaType, Quota]] = {}  # org_id -> quotas
        self._alerts: list[dict] = []

    def set_quota(self, org_id: str, quota_type: QuotaType, limit: int,
                  overage_policy: OveragePolicy = OveragePolicy.BLOCK,
                  alert_threshold: float = 0.8) -> Quota:
        org_quotas = self._quotas.setdefault(org_id, {})
        quota = Quota(quota_type=quota_type, limit=limit,
                      overage_policy=overage_policy, alert_threshold=alert_threshold)
        org_quotas[quota_type] = quota
        return quota

    def consume(self, org_id: str, quota_type: QuotaType, amount: int = 1) -> tuple[bool, str]:
        """Consume quota. Returns (allowed, message)."""
        quota = self._quotas.get(org_id, {}).get(quota_type)
        if not quota:
            return True, "No quota set"

        new_used = quota.used + amount
        if new_used > quota.limit:
            if quota.overage_policy == OveragePolicy.BLOCK:
                return False, f"Quota exceeded: {quota.used}/{quota.limit} {quota_type.value}"
            elif quota.overage_policy == OveragePolicy.THROTTLE:
                quota.used = new_used
                return True, "Throttled: request allowed at reduced priority"

        quota.used = new_used
        if quota.alert_triggered and not any(
            a["org_id"] == org_id and a["type"] == quota_type.value for a in self._alerts
        ):
            self._alerts.append({
                "org_id": org_id, "type": quota_type.value,
                "usage_percent": quota.usage_percent,
                "message": f"{quota_type.value} at {quota.usage_percent}% of limit",
            })
        return True, "OK"

    def get_quota(self, org_id: str, quota_type: QuotaType) -> Quota | None:
        return self._quotas.get(org_id, {}).get(quota_type)

    def get_all_quotas(self, org_id: str) -> list[dict]:
        return [
            {"type": q.quota_type.value, "limit": q.limit, "used": q.used,
             "remaining": q.remaining, "percent": q.usage_percent,
             "over_limit": q.over_limit}
            for q in self._quotas.get(org_id, {}).values()
        ]

    def reset_quota(self, org_id: str, quota_type: QuotaType) -> bool:
        quota = self._quotas.get(org_id, {}).get(quota_type)
        if quota:
            quota.used = 0
            return True
        return False

    def get_alerts(self, org_id: str | None = None) -> list[dict]:
        if org_id:
            return [a for a in self._alerts if a["org_id"] == org_id]
        return list(self._alerts)
