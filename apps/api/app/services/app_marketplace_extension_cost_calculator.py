"""Extension Cost Calculator — estimate costs for extension usage."""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class CostItem:
    name: str
    unit: str
    quantity: float
    unit_price_cents: int
    total_cents: int = 0
    def __post_init__(self):
        self.total_cents = round(self.quantity * self.unit_price_cents)


@dataclass
class CostEstimate:
    items: list[CostItem] = field(default_factory=list)
    discount_pct: float = 0.0

    @property
    def subtotal_cents(self) -> int:
        return sum(i.total_cents for i in self.items)

    @property
    def discount_cents(self) -> int:
        return round(self.subtotal_cents * self.discount_pct / 100)

    @property
    def total_cents(self) -> int:
        return self.subtotal_cents - self.discount_cents


class ExtCostCalculatorService:
    PRICING = {
        "api_calls": ("API Calls", "1K calls", 10),  # 10 cents per 1K
        "compute": ("Compute", "hour", 50),  # 50 cents per hour
        "storage": ("Storage", "GB/month", 25),  # 25 cents per GB
        "bandwidth": ("Bandwidth", "GB", 15),  # 15 cents per GB
    }

    def estimate(self, usage: dict[str, float], discount_pct: float = 0) -> CostEstimate:
        items = []
        for metric, qty in usage.items():
            if metric in self.PRICING:
                name, unit, price = self.PRICING[metric]
                items.append(CostItem(name=name, unit=unit, quantity=qty,
                                      unit_price_cents=price))
        return CostEstimate(items=items, discount_pct=discount_pct)

    def compare_plans(self, usage: dict[str, float]) -> list[dict]:
        plans = [
            {"name": "Free", "discount": 0, "included": {"api_calls": 10, "storage": 1}},
            {"name": "Pro", "discount": 10, "included": {"api_calls": 100, "storage": 10, "compute": 10}},
            {"name": "Enterprise", "discount": 25, "included": {"api_calls": 1000, "storage": 100, "compute": 100, "bandwidth": 100}},
        ]
        results = []
        for plan in plans:
            overage = {}
            for k, v in usage.items():
                included = plan["included"].get(k, 0)
                if v > included:
                    overage[k] = v - included
            est = self.estimate(overage, plan["discount"])
            results.append({"plan": plan["name"], "total_cents": est.total_cents,
                            "overage_items": len(overage)})
        return results
