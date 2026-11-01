"""Usage Quota Dashboard — track and display resource usage vs plan limits."""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class QuotaLimit:
    resource: str
    used: int = 0
    limit: int = 0  # 0 = unlimited
    unit: str = "calls"

    @property
    def percentage(self) -> float:
        if self.limit == 0: return 0.0
        return round(self.used / self.limit * 100, 1)

    @property
    def is_exceeded(self) -> bool:
        return self.limit > 0 and self.used >= self.limit


class UsageQuotaDashboardService:
    def __init__(self):
        self._quotas: dict[str, dict[str, QuotaLimit]] = {}

    def set_limit(self, user_id: str, resource: str, limit: int, unit: str = "calls") -> QuotaLimit:
        if user_id not in self._quotas:
            self._quotas[user_id] = {}
        q = QuotaLimit(resource=resource, limit=limit, unit=unit)
        self._quotas[user_id][resource] = q
        return q

    def record_usage(self, user_id: str, resource: str, amount: int = 1) -> bool:
        q = self._quotas.get(user_id, {}).get(resource)
        if not q: return False
        if q.is_exceeded: return False
        q.used += amount
        return True

    def get_dashboard(self, user_id: str) -> list[QuotaLimit]:
        return list(self._quotas.get(user_id, {}).values())

    def get_warnings(self, user_id: str, threshold: float = 80.0) -> list[QuotaLimit]:
        return [q for q in self.get_dashboard(user_id)
                if q.limit > 0 and q.percentage >= threshold]

    def reset(self, user_id: str, resource: str) -> bool:
        q = self._quotas.get(user_id, {}).get(resource)
        if q:
            q.used = 0
            return True
        return False
