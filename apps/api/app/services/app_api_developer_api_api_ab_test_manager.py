"""App API Developer API A/B Test Manager — manage API A/B experiments."""
from __future__ import annotations
from dataclasses import dataclass, field
import hashlib
import structlog

log = structlog.get_logger()

@dataclass
class ABVariant:
    name: str
    weight: int  # 0-100
    conversions: int = 0
    impressions: int = 0

    @property
    def conversion_rate(self) -> float:
        return round(self.conversions / self.impressions * 100, 2) if self.impressions > 0 else 0.0

@dataclass
class ABTest:
    test_id: str
    endpoint: str
    variants: list[ABVariant]
    status: str = "running"  # "running", "paused", "completed"

    @property
    def winner(self) -> ABVariant | None:
        if self.status != "completed": return None
        return max(self.variants, key=lambda v: v.conversion_rate) if self.variants else None

class AppAPIDeveloperAPIApiABTestManager:
    def __init__(self) -> None:
        self._tests: dict[tuple[str, str], ABTest] = {}

    def create(self, installation_id: str, test_id: str, endpoint: str, variants: list[dict]) -> ABTest:
        if not installation_id: raise ValueError("installation_id is required")
        if len(variants) < 2: raise ValueError("Need at least 2 variants")
        total = sum(v.get("weight", 50) for v in variants)
        if total != 100: raise ValueError(f"Weights must total 100, got {total}")
        key = (installation_id, test_id)
        if key in self._tests: raise ValueError(f"Test {test_id} exists")
        parsed = [ABVariant(name=v["name"], weight=v.get("weight", 50)) for v in variants]
        t = ABTest(test_id=test_id, endpoint=endpoint, variants=parsed)
        self._tests[key] = t
        return t

    def assign(self, installation_id: str, test_id: str, consumer_id: str) -> str:
        t = self._get(installation_id, test_id)
        h = int(hashlib.sha256(f"{test_id}:{consumer_id}".encode()).hexdigest()[:8], 16) % 100
        cumulative = 0
        for v in t.variants:
            cumulative += v.weight
            if h < cumulative:
                v.impressions += 1
                return v.name
        t.variants[-1].impressions += 1
        return t.variants[-1].name

    def convert(self, installation_id: str, test_id: str, variant_name: str) -> None:
        t = self._get(installation_id, test_id)
        for v in t.variants:
            if v.name == variant_name:
                v.conversions += 1
                return
        raise KeyError(f"Variant {variant_name} not found")

    def complete(self, installation_id: str, test_id: str) -> ABTest:
        t = self._get(installation_id, test_id)
        t.status = "completed"
        return t

    def list_tests(self, installation_id: str) -> list[ABTest]:
        return [t for (inst, _), t in self._tests.items() if inst == installation_id]

    def _get(self, installation_id: str, test_id: str) -> ABTest:
        key = (installation_id, test_id)
        t = self._tests.get(key)
        if t is None: raise KeyError(f"Test {test_id} not found")
        return t
