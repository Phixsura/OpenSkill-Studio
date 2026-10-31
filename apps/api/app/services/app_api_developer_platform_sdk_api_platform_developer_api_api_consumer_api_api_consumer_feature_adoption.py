"""API Consumer Feature Adoption — track which API features consumers are using."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class FeatureUsage:
    feature_id: str
    name: str
    adopted_consumers: set[str] = field(default_factory=set)
    total_usage_count: int = 0

    @property
    def adoption_count(self) -> int:
        return len(self.adopted_consumers)

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerFeatureAdoption:
    def __init__(self) -> None:
        self._features: dict[tuple[str, str], FeatureUsage] = {}

    def register_feature(self, installation_id: str, feature_id: str, name: str) -> FeatureUsage:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, feature_id)
        if key not in self._features:
            self._features[key] = FeatureUsage(feature_id=feature_id, name=name)
        return self._features[key]

    def record_usage(self, installation_id: str, feature_id: str, consumer_id: str) -> FeatureUsage:
        key = (installation_id, feature_id)
        f = self._features.get(key)
        if f is None: raise KeyError(f"Feature {feature_id} not found")
        f.adopted_consumers.add(consumer_id)
        f.total_usage_count += 1
        return f

    def adoption_rate(self, installation_id: str, total_consumers: int) -> dict[str, float]:
        if total_consumers == 0: return {}
        return {f.name: round(f.adoption_count / total_consumers * 100, 1)
                for (inst, _), f in self._features.items() if inst == installation_id}

    def least_adopted(self, installation_id: str, limit: int = 5) -> list[FeatureUsage]:
        features = [f for (inst, _), f in self._features.items() if inst == installation_id]
        return sorted(features, key=lambda f: f.adoption_count)[:limit]

    def consumer_features(self, installation_id: str, consumer_id: str) -> list[str]:
        return [f.name for (inst, _), f in self._features.items() if inst == installation_id and consumer_id in f.adopted_consumers]

    def list_features(self, installation_id: str) -> list[FeatureUsage]:
        return [f for (inst, _), f in self._features.items() if inst == installation_id]
