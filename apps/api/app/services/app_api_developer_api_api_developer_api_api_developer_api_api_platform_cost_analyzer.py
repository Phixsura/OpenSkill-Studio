"""App API Developer Platform Cost Analyzer — analyze platform costs by dimension."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class CostBreakdown:
    dimension: str  # "compute", "storage", "bandwidth", "api_calls", "webhooks"
    cost_cents: int = 0
    usage: float = 0.0
    unit: str = ""

@dataclass
class PlatformCostReport:
    period: str
    items: list[CostBreakdown] = field(default_factory=list)

    @property
    def total_cents(self) -> int:
        return sum(i.cost_cents for i in self.items)

    @property
    def top_cost_dimension(self) -> str:
        if not self.items: return ""
        return max(self.items, key=lambda i: i.cost_cents).dimension

class AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiPlatformCostAnalyzer:
    def __init__(self) -> None:
        self._reports: dict[tuple[str, str], PlatformCostReport] = {}

    def record(self, installation_id: str, period: str, items: list[dict]) -> PlatformCostReport:
        if not installation_id: raise ValueError("installation_id is required")
        valid_dims = {"compute", "storage", "bandwidth", "api_calls", "webhooks"}
        parsed = []
        for item in items:
            if item["dimension"] not in valid_dims: raise ValueError(f"Invalid dimension: {item['dimension']}")
            parsed.append(CostBreakdown(dimension=item["dimension"], cost_cents=item.get("cost_cents", 0), usage=item.get("usage", 0), unit=item.get("unit", "")))
        r = PlatformCostReport(period=period, items=parsed)
        self._reports[(installation_id, period)] = r
        return r

    def get(self, installation_id: str, period: str) -> PlatformCostReport | None:
        return self._reports.get((installation_id, period))

    def trend(self, installation_id: str) -> list[PlatformCostReport]:
        reports = [r for (inst, _), r in self._reports.items() if inst == installation_id]
        return sorted(reports, key=lambda r: r.period)

    def total_spend_cents(self, installation_id: str) -> int:
        return sum(r.total_cents for (inst, _), r in self._reports.items() if inst == installation_id)
