"""App API Developer Platform Feature Adoption — track feature adoption across consumers."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class FeatureAdoption:
    feature_name: str
    total_consumers: int = 0
    adopters: int = 0
    first_adopted_at: float = 0.0

    @property
    def adoption_pct(self) -> float:
        return round(self.adopters / self.total_consumers * 100, 1) if self.total_consumers > 0 else 0.0

    @property
    def adoption_tier(self) -> str:
        p = self.adoption_pct
        if p >= 75: return "mainstream"
        if p >= 40: return "early_majority"
        if p >= 15: return "early_adopters"
        return "innovators"

class AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiPlatformFeatureAdoption:
    def __init__(self) -> None:
        self._features: dict[tuple[str, str], FeatureAdoption] = {}

    def track(self, installation_id: str, feature_name: str, total_consumers: int, adopters: int) -> FeatureAdoption:
        if not installation_id: raise ValueError("installation_id is required")
        if adopters > total_consumers: raise ValueError("adopters cannot exceed total")
        key = (installation_id, feature_name)
        f = FeatureAdoption(feature_name=feature_name, total_consumers=total_consumers, adopters=adopters)
        self._features[key] = f
        return f

    def low_adoption(self, installation_id: str, threshold_pct: float = 20) -> list[FeatureAdoption]:
        return [f for (inst, _), f in self._features.items() if inst == installation_id and f.adoption_pct < threshold_pct]

    def by_tier(self, installation_id: str) -> dict[str, int]:
        counts: dict[str, int] = {}
        for (inst, _), f in self._features.items():
            if inst == installation_id: counts[f.adoption_tier] = counts.get(f.adoption_tier, 0) + 1
        return counts

    def all_features(self, installation_id: str) -> list[FeatureAdoption]:
        return sorted([f for (inst, _), f in self._features.items() if inst == installation_id], key=lambda f: f.adoption_pct, reverse=True)
