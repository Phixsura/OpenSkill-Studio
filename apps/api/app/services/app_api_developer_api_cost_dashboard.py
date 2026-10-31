"""App API Developer API Cost Dashboard — unified API cost overview."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class CostDashboard:
    total_cost: float = 0.0
    cost_by_service: dict[str, float] = None
    budget_limit: float = 0.0
    budget_used_pct: float = 0.0
    projected_monthly: float = 0.0
    cost_trend: str = "stable"  # "increasing", "decreasing", "stable"
    currency: str = "USD"

    def __post_init__(self):
        if self.cost_by_service is None:
            self.cost_by_service = {}

    @property
    def over_budget(self) -> bool:
        return self.budget_limit > 0 and self.total_cost > self.budget_limit

class AppAPIDeveloperAPICostDashboard:
    def __init__(self) -> None:
        self._dashboards: dict[str, CostDashboard] = {}

    def update(self, installation_id: str, **kwargs) -> CostDashboard:
        if not installation_id: raise ValueError("installation_id is required")
        if installation_id not in self._dashboards:
            self._dashboards[installation_id] = CostDashboard()
        d = self._dashboards[installation_id]
        for k, v in kwargs.items():
            if hasattr(d, k): setattr(d, k, v)
        return d

    def get(self, installation_id: str) -> CostDashboard:
        return self._dashboards.get(installation_id, CostDashboard())
