"""Extension A/B Test Manager — run experiments on extension listings."""
from __future__ import annotations
from dataclasses import dataclass, field
import hashlib


@dataclass
class Variant:
    variant_id: str
    name: str
    weight: float = 0.5
    impressions: int = 0
    conversions: int = 0

    @property
    def conversion_rate(self) -> float:
        return self.conversions / self.impressions if self.impressions > 0 else 0.0


@dataclass
class ABTest:
    test_id: str
    extension_id: str
    field: str  # title, description, icon, screenshot_order
    variants: list[Variant] = field(default_factory=list)
    active: bool = True


class ExtABTestMgrService:
    def __init__(self):
        self._tests: dict[str, ABTest] = {}
        self._counter = 0

    def create(self, extension_id: str, test_field: str,
               variants: list[tuple[str, str, float]]) -> ABTest:
        self._counter += 1
        tid = f"ab-{self._counter}"
        vs = [Variant(variant_id=v[0], name=v[1], weight=v[2]) for v in variants]
        total_weight = sum(v.weight for v in vs)
        if abs(total_weight - 1.0) > 0.01:
            raise ValueError("Variant weights must sum to 1.0")
        test = ABTest(test_id=tid, extension_id=extension_id,
                      field=test_field, variants=vs)
        self._tests[tid] = test
        return test

    def assign(self, test_id: str, user_id: str) -> str | None:
        test = self._tests.get(test_id)
        if not test or not test.active:
            return None
        h = int(hashlib.md5(f"{test_id}:{user_id}".encode()).hexdigest(), 16)
        bucket = (h % 1000) / 1000.0
        cumulative = 0.0
        for v in test.variants:
            cumulative += v.weight
            if bucket < cumulative:
                v.impressions += 1
                return v.variant_id
        test.variants[-1].impressions += 1
        return test.variants[-1].variant_id

    def record_conversion(self, test_id: str, variant_id: str) -> bool:
        test = self._tests.get(test_id)
        if not test:
            return False
        for v in test.variants:
            if v.variant_id == variant_id:
                v.conversions += 1
                return True
        return False

    def get_results(self, test_id: str) -> dict | None:
        test = self._tests.get(test_id)
        if not test:
            return None
        return {"test_id": test.test_id, "field": test.field,
                "variants": [{"id": v.variant_id, "name": v.name,
                              "impressions": v.impressions,
                              "conversions": v.conversions,
                              "rate": round(v.conversion_rate * 100, 2)}
                             for v in test.variants]}

    def stop(self, test_id: str) -> bool:
        test = self._tests.get(test_id)
        if test:
            test.active = False
            return True
        return False
