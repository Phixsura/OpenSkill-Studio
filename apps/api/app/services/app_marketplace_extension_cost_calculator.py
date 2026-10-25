"""Cost Calculator — estimate and track extension infrastructure costs.

Calculates per-extension infrastructure costs based on compute, storage,
bandwidth, and API usage for billing and cost optimization.
"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class CostBreakdown:
    compute_cents: int = 0
    storage_cents: int = 0
    bandwidth_cents: int = 0
    api_calls_cents: int = 0

    @property
    def total_cents(self) -> int:
        return self.compute_cents + self.storage_cents + self.bandwidth_cents + self.api_calls_cents


# Per-unit pricing in cents
PRICING = {
    "compute_per_minute": 1,      # 1 cent per compute minute
    "storage_per_gb_month": 25,   # 25 cents per GB/month
    "bandwidth_per_gb": 10,       # 10 cents per GB transferred
    "api_per_1000_calls": 5,      # 5 cents per 1000 API calls
}


class CostCalculator:
    """Calculates extension infrastructure costs."""

    def __init__(self, pricing: dict | None = None):
        self._pricing = pricing or dict(PRICING)
        self._history: dict[str, list[CostBreakdown]] = {}

    def calculate(self, compute_minutes: float, storage_gb: float,
                  bandwidth_gb: float, api_calls: int) -> CostBreakdown:
        """Calculate cost breakdown for given usage."""
        return CostBreakdown(
            compute_cents=int(compute_minutes * self._pricing["compute_per_minute"]),
            storage_cents=int(storage_gb * self._pricing["storage_per_gb_month"]),
            bandwidth_cents=int(bandwidth_gb * self._pricing["bandwidth_per_gb"]),
            api_calls_cents=int(api_calls / 1000 * self._pricing["api_per_1000_calls"]),
        )

    def record(self, extension_id: str, breakdown: CostBreakdown) -> None:
        self._history.setdefault(extension_id, []).append(breakdown)

    def get_total(self, extension_id: str) -> int:
        """Get total cost in cents for an extension."""
        return sum(b.total_cents for b in self._history.get(extension_id, []))

    def get_average_monthly(self, extension_id: str) -> int:
        history = self._history.get(extension_id, [])
        if not history:
            return 0
        return sum(b.total_cents for b in history) // len(history)

    def estimate_monthly(self, daily_compute_min: float, storage_gb: float,
                         daily_bandwidth_gb: float, daily_api_calls: int) -> dict:
        """Estimate monthly cost from daily usage."""
        monthly = self.calculate(
            daily_compute_min * 30, storage_gb,
            daily_bandwidth_gb * 30, daily_api_calls * 30,
        )
        return {
            "compute": monthly.compute_cents,
            "storage": monthly.storage_cents,
            "bandwidth": monthly.bandwidth_cents,
            "api_calls": monthly.api_calls_cents,
            "total_cents": monthly.total_cents,
            "total_dollars": round(monthly.total_cents / 100, 2),
        }

    def compare_costs(self, ext_a: str, ext_b: str) -> dict:
        """Compare total costs between two extensions."""
        total_a = self.get_total(ext_a)
        total_b = self.get_total(ext_b)
        return {
            "extension_a": {"id": ext_a, "total_cents": total_a},
            "extension_b": {"id": ext_b, "total_cents": total_b},
            "difference_cents": abs(total_a - total_b),
            "cheaper": ext_a if total_a <= total_b else ext_b,
        }

    def get_cost_breakdown(self, extension_id: str) -> dict:
        history = self._history.get(extension_id, [])
        if not history:
            return {"compute": 0, "storage": 0, "bandwidth": 0, "api_calls": 0, "total": 0}
        return {
            "compute": sum(b.compute_cents for b in history),
            "storage": sum(b.storage_cents for b in history),
            "bandwidth": sum(b.bandwidth_cents for b in history),
            "api_calls": sum(b.api_calls_cents for b in history),
            "total": sum(b.total_cents for b in history),
        }
